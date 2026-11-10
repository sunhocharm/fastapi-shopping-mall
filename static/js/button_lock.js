class ButtonLocker {
  constructor(buttonElement, loadingText = "처리 중...") {
    this.btn = buttonElement;
    if (this.btn) {
      this.originalText = this.btn.innerText;
      this.loadingText = loadingText;
    }
  }

  lock() {
    if (!this.btn) return;
    this.btn.disabled = true;
    this.btn.innerText = this.loadingText;

    // 핵심: 브라우저가 disabled된 버튼의 마우스 커서 감지를 차단하는 것을 방지합니다.
    this.btn.style.pointerEvents = "auto";
    // 이제 금지 표시 커서가 정상적으로 화면에 출력됩니다.
    this.btn.style.cursor = "not-allowed";
  }

  unlock() {
    if (!this.btn) return;
    this.btn.disabled = false;
    this.btn.innerText = this.originalText;

    // 상태 복구 시 스타일 초기화
    this.btn.style.pointerEvents = "";
    this.btn.style.cursor = "";
  }
}
