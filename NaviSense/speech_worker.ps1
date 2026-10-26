
Add-Type -AssemblyName System.Speech

$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
$synth.Volume = 100
$synth.Rate = 0

try {
    while ($true) {
        $line = [Console]::ReadLine()

        if ($null -eq $line) {
            break
        }

        if ($line -eq "__CANCEL__") {
            $synth.SpeakAsyncCancelAll()
            continue
        }

        if ($line -eq "__QUIT__") {
            $synth.SpeakAsyncCancelAll()
            break
        }

        if (-not [string]::IsNullOrWhiteSpace($line)) {
            $synth.SpeakAsync($line)
        }
    }
}
catch {
    [Console]::Error.WriteLine($_.Exception.Message)
}
finally {
    $synth.SpeakAsyncCancelAll()
    $synth.Dispose()
}
