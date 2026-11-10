/**
 * 폼 내부의 입력 요소들에 데이터를 자동으로 매핑하는 유틸리티 함수
 * @param {string|HTMLElement} formSelector - 대상 폼의 CSS 선택자 또는 Element
 * @param {Object} data - 서버에서 넘어온 데이터 객체 (JSON)
 * @param {Object} customMappings - [선택] id/name과 데이터 key가 다를 때의 예외 매핑 규칙
 */

export function autoFillForm(form, data, names_to_skip, customMappings = {}) {
  if (!data) return;

  if (!form) return;

  // 폼 내의 모든 입력 엘리먼트 수집 (input, select, textarea)
  const formElements = form.querySelectorAll("input, select, textarea");

  formElements.forEach((element) => {
    // 1. 기준이 될 key 추출 (id 또는 name)
    const elementKey = element.id || element.name;
    if (!elementKey) return;
    if (names_to_skip.includes(elementKey)) return;

    // 2. 예외 매핑 규칙이 있다면 적용, 없다면 기본 key 사용
    // 예: customMappings가 { 'category': 'category_id' } 이면, elementKey가 'category'일 때 data['category_id']를 찾음
    const dataKey = customMappings[elementKey] || elementKey;
    let dataValue = data[dataKey];

    // 3. 데이터에 해당 값이 존재하는 경우 매핑 수행 (버튼 등은 제외)
    if (dataValue !== undefined && dataValue !== null) {
      if (element.type === "checkbox") {
        element.checked = !!dataValue;
      } else if (element.type === "radio") {
        element.checked = element.value === String(dataValue);
      } else {
        element.value = dataValue;
      }
    }
  });
}
