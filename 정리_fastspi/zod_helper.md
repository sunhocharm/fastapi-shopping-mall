## 1. 특히 Zod 에러와 Custom 에러를 별도 객체로 관리하도록 변경했습니다

let zod_field_errors = {};
let custom_field_errors = {};

## 2. form.html에서 커스텀 검증 등록하기

이번에 구현한 핵심 API입니다.

```js
zodSetCustomValidators({
  original_price: {
    dependsOn: ["price", "original_price"],

    validate: (data) => {
      if (!data.original_price?.trim()) return null;

      if (
        !/^\d+$/.test(data.price || "") ||
        !/^\d+$/.test(data.original_price)
      ) {
        return null;
      }

      return Number(data.original_price) > Number(data.price)
        ? null
        : "정가는 판매가보다 커야 합니다.";
    },
  },
});
```

## 3. 다른 검증에도 재사용하기

이제 새로운 검증을 추가할 때 유틸리티 코드를 수정할 필요가 없습니다.

### 예시 A. 비밀번호 확인

```js
zodSetCustomValidators({
  passwordConfirm: {
    dependsOn: ["password", "passwordConfirm"],

    validate: (data) => {
      return data.password === data.passwordConfirm
        ? null
        : "비밀번호가 일치하지 않습니다.";
    },
  },
});
```

### 예시 B. 시작일과 종료일 비교

```js
zodSetCustomValidators({
  endDate: {
    dependsOn: ["startDate", "endDate"],

    validate: (data) => {
      if (!data.startDate || !data.endDate) return null;

      return new Date(data.endDate) >= new Date(data.startDate)
        ? null
        : "종료일은 시작일보다 빠를 수 없습니다.";
    },
  },
});
```

### 여러 검증 규칙도 한 번에 등록할 수 있습니다.

```js
zodSetCustomValidators({
    original_price: { ... },
    passwordConfirm: { ... },
    endDate: { ... }
});
```

## 4. 폼 제출 코드도 간결해졌습니다.

기존에는 Zod 검증 결과를 직접 확인하고 에러를 표시해야 했습니다.

이제는 다음과 같이 사용할 수 있습니다.

```js
form.addEventListener("submit", (e) => {
  e.preventDefault();

  if (zodValidateAllFields()) {
    form.submit();
  }
});
```

## 5. 최종적으로 얻는 장점

재사용 가능한 구조
앞으로 검증할 항목이 추가되어도 zod_utils.js를 수정할 필요가 없습니다.

예를 들어 다음과 같은 검증을 모두 동일한 패턴으로 처리할 수 있습니다.

- 상품의 정가와 판매가 비교
- 비밀번호와 비밀번호 확인
- 시작일과 종료일 비교
- 최소 주문 수량과 최대 주문 수량 비교
- 할인율과 할인 금액의 관계
- 최소 나이와 최대 나이 비교

### 한 가지 참고:

이 구조는 입력 중에는 변경된 필드와 그 필드에 의존하는 커스텀 검증을 갱신하고, 제출 시에는 모든 검증을 실행합니다.
또한 실제 데이터 저장 시에는 서버에서도 동일한 비즈니스 규칙을 검증해야 합니다.
