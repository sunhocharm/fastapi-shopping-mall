"use strict";

export const zodPasswordValidator = {
  dependsOn: ["password"], // password 필드가 변경될 때 검증 유발
  validate: (data) => {
    const val = data.password || "";

    // 1. 최소/최대 자릿수 검증
    if (val.length < 8) {
      return "최소 8자리 이상이어야 합니다.";
    }
    if (val.length > 20) {
      return "최대 20자리 이하이어야 합니다.";
    }

    // 2. 영문 대문자 포함 여부 검증
    if (!/[A-Z]/.test(val)) {
      return "영문 대문자가 1개 이상 포함되어야 합니다.";
    }

    // 3. 영문 소문자 포함 여부 검증
    if (!/[a-z]/.test(val)) {
      return "영문 소문자가 1개 이상 포함되어야 합니다.";
    }

    // 4. 숫자 포함 여부 검증
    if (!/[0-9]/.test(val)) {
      return "숫자가 1개 이상 포함되어야 합니다.";
    }

    // 5. 특수문자 포함 여부 검증
    if (!/[^a-zA-Z0-9]/.test(val)) {
      return "특수문자가 1개 이상 포함되어야 합니다.";
    }

    return null; // 모든 조건을 통과하면 에러 없음(null) 반환
  },
};

export const zodPhoneValidator = {
  dependsOn: ["phone"], // phone 필드가 변경될 때 검증 유발
  validate: (data) => {
    const val = data.phone;

    // 3. 완전히 비어있거나 생략된 경우(선택 필드) 통과
    if (!val || val === "") return null;

    // 1. 하이픈(-) 포함 여부 및 전체적인 형태 검증
    if (!/^[0-9-]+$/.test(val)) {
      return "숫자와 하이픈(-)만 입력할 수 있습니다.";
    }

    const parts = val.split("-");
    if (parts.length !== 3) {
      return "전화번호는 '숫자-숫자-숫자' 형식이어야 합니다.";
    }

    // 2. 각 파트별 자릿수 정밀 검증
    if (parts[0]?.length !== 2 && parts[0]?.length !== 3) {
      return "첫 번째 부분은 2자리 또는 3자리 숫자여야 합니다. (예: 010, 02)";
    }
    if (parts[1]?.length !== 3 && parts[1]?.length !== 4) {
      return "두 번째 부분은 3자리 또는 4자리 숫자여야 합니다.";
    }
    if (parts[2]?.length !== 4) {
      return "마지막 부분은 반드시 4자리 숫자여야 합니다.";
    }

    return null; // 모든 검증을 통과하면 에러 없음(null) 반환
  },
};

export function zodShowButtonError(buttonElement) {
  // 1. 에러 메시지 생성
  const errorDiv = Object.assign(document.createElement("div"), {
    className: "button-error-message",
    textContent: "입력 오류",
  });

  // 2. 버튼 위치 계산 (스크롤 고려)
  const rect = buttonElement.getBoundingClientRect();

  errorDiv.style.position = "absolute";
  errorDiv.style.left = `${rect.left + window.scrollX + rect.width / 2}px`;
  errorDiv.style.top = `${rect.top + window.scrollY}px`;
  errorDiv.style.transform = "translate(-50%, -100%) translateY(-8px)";

  // 3. 문서에 추가
  document.body.appendChild(errorDiv);

  // 4. 1초 뒤 사라지는 애니메이션 후 제거
  setTimeout(() => {
    errorDiv.style.opacity = "0";
    errorDiv.style.transition = "opacity 0.3s ease";
    setTimeout(() => errorDiv.remove(), 300);
  }, 500);
}
