"use strict";

// Zod 기본 검증과 필드 간 관계를 확인하는 커스텀 검증을 함께 관리합니다.
let zod_schema = null;
let zod_form = null;
let zod_field_names = [];
let zod_custom_validators = {};

// 에러를 검증 종류별로 분리해 두어 한쪽 검증이 다른 쪽 에러를 지우지 않게 합니다.
let zod_field_errors = {};
let custom_field_errors = {};

function getFormDataObject() {
  const formData = new FormData(zod_form);
  return Object.fromEntries(formData.entries());
}

function getZodFieldErrors(data) {
  const result = zod_schema.safeParse(data);
  return {
    result,
    errors: result.success ? {} : result.error.flatten().fieldErrors,
  };
}

// 지정한 필드의 Zod 에러와 커스텀 에러를 합쳐 화면에 표시합니다.
function renderFieldError(field_name) {
  const messages = [
    ...(zod_field_errors[field_name] || []),
    ...(custom_field_errors[field_name]
      ? [custom_field_errors[field_name]]
      : []),
  ];

  const error_div = document.getElementById(`${field_name}Error`);
  const input_field = document.getElementById(field_name);

  if (!error_div || !input_field) return;

  error_div.textContent = messages[0] || "";
  input_field.classList.toggle("error-input", messages.length > 0);
}

function updateCustomValidator(field_name, data) {
  const validator = zod_custom_validators[field_name];
  if (!validator) return;

  const message = validator.validate(data);
  if (typeof message === "string" && message.length > 0) {
    custom_field_errors[field_name] = message;
  } else {
    delete custom_field_errors[field_name];
  }

  renderFieldError(field_name);
}

// 입력 중에는 변경된 필드의 Zod 에러와, 해당 필드에 의존하는 커스텀 검증만 갱신합니다.
function zodValidateEachField(field_name) {
  const data = getFormDataObject();
  const { errors } = getZodFieldErrors(data);

  if (errors[field_name]) {
    zod_field_errors[field_name] = errors[field_name];
  } else {
    delete zod_field_errors[field_name];
  }
  renderFieldError(field_name);

  // 예: price가 바뀌면 price에 의존하는 original_price 검증도 다시 실행합니다.
  Object.entries(zod_custom_validators).forEach(([target_field, validator]) => {
    const dependencies = validator.dependsOn || [target_field];
    if (dependencies.includes(field_name)) {
      updateCustomValidator(target_field, data);
    }
  });
}

// 폼 제출 시 모든 Zod 검증과 커스텀 검증을 실행합니다.
function zodValidateAllFields() {
  const data = getFormDataObject();
  const { result, errors } = getZodFieldErrors(data);

  zod_field_errors = { ...errors };
  custom_field_errors = {};

  Object.entries(zod_custom_validators).forEach(([field_name, validator]) => {
    const message = validator.validate(data);
    if (typeof message === "string" && message.length > 0) {
      custom_field_errors[field_name] = message;
    }
  });

  zod_field_names.forEach(renderFieldError);

  return result.success && Object.keys(custom_field_errors).length === 0;
}

// ------------------------------------------------------------------------- //
// --- 설정 및 이벤트 등록 함수 ---------------------------------------------- //
// ------------------------------------------------------------------------- //
function zodSetSchema(arg_zod_schema) {
  zod_schema = arg_zod_schema;
}

function zodSetFormAndFieldNames(arg_form, arg_field_names) {
  zod_form = arg_form;
  zod_field_names = arg_field_names;
}

// 커스텀 검증기 형식:
// {
//   대상필드: {
//     dependsOn: ['서로', '관련된', '필드'],
//     validate: (formData) => 에러메시지 또는 null
//   }
// }
function zodSetCustomValidators(validators = {}) {
  zod_custom_validators = validators;
  custom_field_errors = {};
}

function zodAddEventListenerOnEachZodField() {
  zod_field_names.forEach((field_name) => {
    const input_element = document.getElementById(field_name);
    if (input_element) {
      input_element.addEventListener("input", () => {
        zodValidateEachField(field_name);
      });
      input_element.addEventListener("change", () => {
        zodValidateEachField(field_name);
      });
    }
  });
}

// 기존 호출부와의 호환성을 위해 유지합니다.
function zodDisplayAllErrors(zodError) {
  zod_field_errors = zodError.flatten().fieldErrors;
  zod_field_names.forEach(renderFieldError);
}

function zodClearAllErrors() {
  zod_field_errors = {};
  custom_field_errors = {};
  zod_field_names.forEach(renderFieldError);
}

// 파일 맨 아래에 추가
export default {
  zodSetSchema,
  zodSetFormAndFieldNames,
  zodAddEventListenerOnEachZodField,
  zodSetCustomValidators,
  zodValidateAllFields,
};
