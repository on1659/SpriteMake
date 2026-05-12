param(
  [switch]$Short
)

$OutputEncoding = [System.Text.UTF8Encoding]::new()
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()

$long = @"
생성 방식부터 정할게요.

1. Codex로 바로 생성
   - API key 없이 이 Codex 세션의 이미지 생성 기능으로 바로 시도합니다.
   - 모델을 gpt-image-2로 강제하거나 검증하지는 못합니다.
   - 결과물은 generated/의 검수 대상 시안으로 보고, QA 통과 전에는 final/로 옮기지 않습니다.

2. gpt-image-2 엄격 생성
   - 제가 gpt-image-2용 프롬프트를 만들어드립니다.
   - 실제 이미지는 ChatGPT 웹이나 API key가 있는 외부 생성 화면에 직접 입력해야 합니다.
   - 이 프로젝트에는 API key를 저장하거나 사용하지 않습니다.

3. Codex로 세팅만
   - 폴더, MD 요청서, 프롬프트, manifest, QA, preview tool만 세팅합니다.
   - 실제 이미지는 생성하지 않습니다.

어느 쪽으로 할까요?
"@

$shortText = "생성 방식을 골라주세요: 1) Codex로 바로 생성(API key 없음, 모델 미검증) 2) gpt-image-2 엄격 생성(ChatGPT 웹/외부 API 환경) 3) Codex로 세팅만 하기"

if ($Short) {
  Write-Output $shortText
} else {
  Write-Output $long.Trim()
}


