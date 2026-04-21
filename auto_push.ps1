while ($true) {
    Write-Host "Waiting 10 minutes before next auto-push..."
    Start-Sleep -Seconds 600

    $status = git status --porcelain
    if ($status) {
        Write-Host "Changes detected. Pushing to repository..."
        git add .
        git commit -m "Auto-commit: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
        git push
        Write-Host "Push complete!"
    } else {
        Write-Host "No changes detected. Skipping push."
    }
}
