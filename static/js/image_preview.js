/**
 * 이미지 파일 선택, 드래그 앤 드롭, 미리보기 및 삭제를 처리하는 유틸리티.
 *
 * 사용 예:
 * import { initImagePreview } from '/static/js/image_preview.js';
 *
 * initImagePreview({
 *     imageInput: document.getElementById('image_input_ctrl'),
 *     dropZone: document.getElementById('image_drop_zone'),
 *     previewContainer: document.getElementById('image_preview_container'),
 *     maxFileSize: 5 * 1024 * 1024
 * });
 */
export function initImagePreview({
  imageInput,
  dropZone,
  previewContainer,
  maxFileSize = 5 * 1024 * 1024,
  onError = (message) => alert(message),
} = {}) {
  if (!imageInput || !dropZone || !previewContainer) {
    throw new Error(
      "initImagePreview: imageInput, dropZone, previewContainer 요소가 필요합니다.",
    );
  }

  let selectedFiles = [];
  const previewUrls = new Map();

  // 파일 선택 및 드롭 파일을 동일한 처리 경로로 전달합니다.
  function handleFiles(fileList) {
    Array.from(fileList || []).forEach((file) => {
      if (!file.type.startsWith("image/")) {
        return;
      }

      if (file.size > maxFileSize) {
        onError(
          `"${file.name}" 파일이 크기 제한(${formatFileSize(maxFileSize)})을 초과하여 제외되었습니다.`,
        );
        return;
      }

      const isDuplicate = selectedFiles.some(
        (selectedFile) =>
          selectedFile.name === file.name &&
          selectedFile.size === file.size &&
          selectedFile.lastModified === file.lastModified,
      );

      if (isDuplicate) {
        return;
      }

      selectedFiles.push(file);
      createPreviewCard(file);
    });

    syncInputFiles();
  }

  function createPreviewCard(file) {
    const col = document.createElement("div");
    col.className = "col position-relative";

    const card = document.createElement("div");
    card.className = "card h-100 overflow-hidden shadow-sm";

    const image = document.createElement("img");
    const imageUrl = URL.createObjectURL(file);
    const fileKey = createFileKey(file);

    image.src = imageUrl;
    image.alt = file.name;
    image.className = "card-img-top object-fit-cover";
    image.height = 120;

    const deleteButton = document.createElement("button");
    deleteButton.type = "button";
    deleteButton.className =
      "btn btn-danger btn-sm position-absolute top-0 end-0 m-1 rounded-circle p-1 line-height-1 btn-delete";
    deleteButton.style.cssText =
      "width: 24px; height: 24px; line-height: 12px;";
    deleteButton.textContent = "×";
    deleteButton.setAttribute("aria-label", `${file.name} 미리보기 삭제`);

    deleteButton.addEventListener("click", () => {
      selectedFiles = selectedFiles.filter(
        (selectedFile) => selectedFile !== file,
      );

      URL.revokeObjectURL(imageUrl);
      previewUrls.delete(file);
      col.remove();
      syncInputFiles();
    });

    card.append(image);
    col.append(card, deleteButton);
    previewContainer.appendChild(col);
    previewUrls.set(file, imageUrl);
    col.dataset.fileId = fileKey;
  }

  function syncInputFiles() {
    const dataTransfer = new DataTransfer();

    selectedFiles.forEach((file) => {
      dataTransfer.items.add(file);
    });

    imageInput.files = dataTransfer.files;
  }

  function handleInputChange() {
    handleFiles(imageInput.files);
  }

  function handleDragOver(event) {
    event.preventDefault();
    dropZone.classList.add("bg-secondary-subtle");
  }

  function handleDragLeave(event) {
    event.preventDefault();
    dropZone.classList.remove("bg-secondary-subtle");
  }

  function handleDrop(event) {
    event.preventDefault();
    dropZone.classList.remove("bg-secondary-subtle");
    handleFiles(event.dataTransfer?.files);
  }

  function formatFileSize(bytes) {
    const megabytes = bytes / (1024 * 1024);
    return `${Number.isInteger(megabytes) ? megabytes : megabytes.toFixed(1)}MB`;
  }

  function createFileKey(file) {
    return `${file.name}-${file.size}-${file.lastModified}`;
  }

  imageInput.addEventListener("change", handleInputChange);
  dropZone.addEventListener("dragenter", handleDragOver);
  dropZone.addEventListener("dragover", handleDragOver);
  dropZone.addEventListener("dragleave", handleDragLeave);
  dropZone.addEventListener("drop", handleDrop);

  // 호출 측에서 필요하면 정리 및 현재 선택 파일 조회가 가능합니다.
  return {
    getSelectedFiles: () => [...selectedFiles],
    destroy() {
      imageInput.removeEventListener("change", handleInputChange);
      dropZone.removeEventListener("dragenter", handleDragOver);
      dropZone.removeEventListener("dragover", handleDragOver);
      dropZone.removeEventListener("dragleave", handleDragLeave);
      dropZone.removeEventListener("drop", handleDrop);

      previewUrls.forEach((url) => URL.revokeObjectURL(url));
      previewUrls.clear();
    },
  };
}
