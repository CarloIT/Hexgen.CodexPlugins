[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$repositoryRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$utf8 = New-Object System.Text.UTF8Encoding($false, $true)

function Assert-Condition {
    param([bool]$Condition, [string]$Message)
    if (-not $Condition) { throw $Message }
}

function Read-Utf8Text {
    param([string]$Path)
    Assert-Condition (Test-Path -LiteralPath $Path -PathType Leaf) "Missing file: $Path"
    $bytes = [System.IO.File]::ReadAllBytes($Path)
    Assert-Condition (-not ($bytes.Length -ge 3 -and $bytes[0] -eq 239 -and $bytes[1] -eq 187 -and $bytes[2] -eq 191)) "UTF-8 BOM found: $Path"
    $content = $utf8.GetString($bytes)
    Assert-Condition (-not ($content.Contains("`r`n") -and [regex]::IsMatch($content, '(?<!\r)\n'))) "Mixed line endings: $Path"
    Assert-Condition (-not [regex]::IsMatch($content, '\r(?!\n)')) "Bare CR found: $Path"
    return $content
}

function Resolve-RepositoryPath {
    param([string]$BasePath, [string]$RelativePath)
    Assert-Condition (-not [System.IO.Path]::IsPathRooted($RelativePath)) "Expected relative path: $RelativePath"
    $resolved = [System.IO.Path]::GetFullPath((Join-Path $BasePath $RelativePath))
    Assert-Condition ($resolved.StartsWith($repositoryRoot + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase)) "Path escapes repository: $RelativePath"
    return $resolved
}

$marketplacePath = Join-Path $repositoryRoot '.agents/plugins/marketplace.json'
$marketplace = (Read-Utf8Text $marketplacePath) | ConvertFrom-Json
Assert-Condition ($marketplace.name -eq 'hexgen-team') 'Unexpected marketplace name.'
Assert-Condition (-not [string]::IsNullOrWhiteSpace($marketplace.interface.displayName)) 'Missing marketplace display name.'
$expectedPlugins = @{
    'hexgen-software-engineering' = @('dev-plan', 'dotnet-backend-standards', 'manual-acceptance-guide')
    'hexgen-productivity' = @('grill-me-single', 'grill-me')
}
$actualPlugins = @($marketplace.plugins | Select-Object -ExpandProperty name)
Assert-Condition (@(Compare-Object @($expectedPlugins.Keys) $actualPlugins).Count -eq 0) 'Unexpected plugin entry set.'
$textFiles = @($marketplacePath)
$textFiles += @(Get-ChildItem -LiteralPath $PSScriptRoot -File | Select-Object -ExpandProperty FullName)
$totalSkills = 0
foreach ($entry in $marketplace.plugins) {
    Assert-Condition ($entry.source.source -eq 'local') 'Expected repository-local plugin source.'
    Assert-Condition ($entry.source.path -eq ('./plugins/' + $entry.name)) 'Unexpected plugin source path.'
    Assert-Condition ($entry.policy.installation -in @('AVAILABLE', 'INSTALLED_BY_DEFAULT', 'NOT_AVAILABLE')) 'Invalid installation policy.'
    Assert-Condition ($entry.policy.authentication -in @('ON_INSTALL', 'ON_USE')) 'Invalid authentication policy.'
    Assert-Condition ($entry.category -eq 'Productivity') 'Unexpected marketplace category.'

    $pluginRoot = Resolve-RepositoryPath $repositoryRoot $entry.source.path
    $manifestPath = Join-Path $pluginRoot '.codex-plugin/plugin.json'
    $manifestText = Read-Utf8Text $manifestPath
    $manifest = $manifestText | ConvertFrom-Json
    Assert-Condition ($manifest.name -eq $entry.name) 'Plugin name and marketplace entry differ.'
    Assert-Condition ((Split-Path $pluginRoot -Leaf) -eq $manifest.name) 'Plugin directory and manifest name differ.'
    Assert-Condition ($manifest.version -cmatch '^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(-[0-9A-Za-z.-]+)?(\+[0-9A-Za-z.-]+)?$') 'Invalid version format.'
    Assert-Condition (-not [string]::IsNullOrWhiteSpace($manifest.description)) 'Missing plugin description.'
    Assert-Condition (-not [string]::IsNullOrWhiteSpace($manifest.author.name)) 'Missing plugin author.'
    Assert-Condition ($manifest.skills -eq './skills/') 'Unexpected skill directory.'
    Assert-Condition (-not $manifestText.Contains('[TODO:')) 'Unfinished manifest placeholder.'
    foreach ($field in @('displayName', 'shortDescription', 'longDescription', 'developerName', 'category', 'defaultPrompt')) {
        Assert-Condition (-not [string]::IsNullOrWhiteSpace($manifest.interface.$field)) "Missing interface field: $field"
    }
    Assert-Condition ($null -ne $manifest.interface.capabilities) 'Missing capabilities array.'
    foreach ($field in @('mcpServers', 'apps', 'hooks')) {
        Assert-Condition (-not ($manifest.PSObject.Properties.Name -contains $field)) "Unexpected integration in skills-only plugin: $field"
    }

    $skillsRoot = Join-Path $pluginRoot 'skills'
    $expectedSkills = $expectedPlugins[$entry.name]
    $actualSkills = @(Get-ChildItem -LiteralPath $skillsRoot -Directory | Select-Object -ExpandProperty Name)
    Assert-Condition (@(Compare-Object $expectedSkills $actualSkills).Count -eq 0) 'Unexpected skill directory set.'
    foreach ($skillName in $expectedSkills) {
        $skillRoot = Join-Path $skillsRoot $skillName
        $skillText = Read-Utf8Text (Join-Path $skillRoot 'SKILL.md')
        $frontmatter = [regex]::Match($skillText, '\A---\r?\n(?<yaml>[\s\S]*?)\r?\n---(?:\r?\n|$)')
        Assert-Condition $frontmatter.Success "Missing frontmatter: $skillName"
        $header = $frontmatter.Groups['yaml'].Value
        Assert-Condition ([regex]::IsMatch($header, '(?m)^name:[ \t]*' + [regex]::Escape($skillName) + '[ \t]*\r?$')) "Skill name differs from directory: $skillName"
        Assert-Condition ([regex]::IsMatch($header, '(?m)^description:[ \t]*\S')) "Missing description: $skillName"
        $uiText = Read-Utf8Text (Join-Path $skillRoot 'agents/openai.yaml')
        foreach ($field in @('display_name', 'short_description', 'default_prompt')) {
            Assert-Condition ([regex]::IsMatch($uiText, '(?m)^[ \t]+' + $field + ':[ \t]*\S')) "Missing UI field $field in $skillName"
        }
    }
    $totalSkills += $expectedSkills.Count
    $textFiles += @(Get-ChildItem -LiteralPath $pluginRoot -File -Recurse -Force | Select-Object -ExpandProperty FullName)
    Write-Output "PASS: plugin $($manifest.name) $($manifest.version); $($expectedSkills.Count) skills."
}
foreach ($fileName in @('README.md', 'AGENTS.md', 'CHANGELOG.md', '.gitattributes')) {
    $textFiles += Join-Path $repositoryRoot $fileName
}
$localLinks = 0
foreach ($textPath in $textFiles) {
    $text = Read-Utf8Text $textPath
    if ([System.IO.Path]::GetExtension($textPath) -ne '.md') { continue }
    foreach ($match in [regex]::Matches($text, '\]\((?<target>[^\s)]+)\)')) {
        $target = $match.Groups['target'].Value
        if ($target -match '^(https?://|#|mailto:)') { continue }
        $target = [System.Uri]::UnescapeDataString(($target -split '#', 2)[0])
        if ([string]::IsNullOrWhiteSpace($target)) { continue }
        $resolved = Resolve-RepositoryPath (Split-Path $textPath -Parent) $target
        Assert-Condition (Test-Path -LiteralPath $resolved -PathType Leaf) "Broken local reference in ${textPath}: $target"
        $localLinks++
    }
}

Write-Output "PASS: marketplace $($marketplace.name); $($actualPlugins.Count) plugins."
Write-Output "PASS: $totalSkills skills; $($textFiles.Count) text files; $localLinks local references."
Write-Output 'Scope: structure, local references, UTF-8 and consistent line endings; not full YAML/schema or skill behavior validation.'
