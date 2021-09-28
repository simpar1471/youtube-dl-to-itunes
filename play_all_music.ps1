# Set-ExecutionPolicy Restricted
# Set-ExecutionPolicy RemoteSigned
Set-ExecutionPolicy Bypass
Write-Host "Playing all music in folder"
# Search for iTunes COM object -->
Get-CimInstance Win32_COMSetting|Select-Object ProgId, Caption|Where-Object Caption -ILike "*itunes*"

# instantiate the object - the .<number> at the end may reference a version
$itunes = New-Object -ComObject iTunes.Application.1
$itunes.Mute = $True

# play any file from your hard drive
$fileext = ".mp3"
Foreach ($file IN Get-ChildItem $PSScriptRoot)
{
    $filename = $PSScriptRoot+"\"+$file
    if ($filename.contains($fileext))
    {
        Write-Host $filename
        $itunes.PlayFile($filename)
    }
}
Start-Sleep -Seconds 2
$itunes.Quit()