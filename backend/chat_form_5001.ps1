param(
  # 注意：为兼容 Windows PowerShell 对脚本文件编码的解析，这里默认值仅使用 ASCII。
  # 你可以通过 -Message 传入任意中文内容。
  [string]$Message = "test message",
  [string]$SessionId = "ps_form",
  [string]$PersonaId = "warm_partner",
  [string]$BaseUrl = "http://127.0.0.1:5001"
)

$msg = [System.Uri]::EscapeDataString($Message)
$body = "message=$msg&session_id=$SessionId&persona_id=$PersonaId"

Invoke-WebRequest -UseBasicParsing -Method POST `
  -Uri "$BaseUrl/api/chat" `
  -ContentType "application/x-www-form-urlencoded" `
  -Body $body `
  -TimeoutSec 60 | Select-Object -ExpandProperty Content


