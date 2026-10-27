$ErrorActionPreference = 'Stop'
$taskRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$documentPath = [System.IO.Path]::GetFullPath((Join-Path $taskRoot 'AI招聘低分成因诊断_研究计划_20261027.docx'))
$renderFolder = [System.IO.Path]::GetFullPath((Join-Path $taskRoot 'tmp/render'))
if (-not $documentPath.StartsWith($taskRoot + [System.IO.Path]::DirectorySeparatorChar)) { throw 'Unexpected input path' }
if (-not $renderFolder.StartsWith($taskRoot + [System.IO.Path]::DirectorySeparatorChar)) { throw 'Unexpected output path' }
if (-not (Test-Path -LiteralPath $documentPath -PathType Leaf)) { throw 'Missing proposal' }
New-Item -ItemType Directory -Path $renderFolder -Force | Out-Null
$pdfPath = Join-Path $renderFolder 'proposal_word_render.pdf'
$application = $null
$document = $null
$ownsEmptyInstance = $false
try {
    $application = New-Object -ComObject Word.Application
    if ($application.Documents.Count -ne 0) { throw 'Refusing to alter a Word session with existing documents' }
    $ownsEmptyInstance = $true
    $application.Visible = $false
    $application.DisplayAlerts = 0
    $application.AutomationSecurity = 3
    $document = $application.Documents.Open($documentPath, $false, $true, $false)
    $document.Fields.Update() | Out-Null
    $document.Repaginate()
    $pages = $document.ComputeStatistics(2)
    $document.ExportAsFixedFormat($pdfPath, 17)
    $result = @{ renderer = 'Microsoft Word COM'; pages = $pages; input = $documentPath; output = $pdfPath }
    $result | ConvertTo-Json -Compress
} finally {
    if ($null -ne $document) {
        $document.Close(0)
        [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($document)
    }
    if ($null -ne $application) {
        if ($ownsEmptyInstance -and $application.Documents.Count -eq 0) { $application.Quit(0) }
        [void][System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($application)
    }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}
