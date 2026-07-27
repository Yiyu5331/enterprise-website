(function () {
  'use strict';

  function csrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
  }

  async function uploadImage(file, kind, alt) {
    var data = new FormData();
    data.append('image', file);
    data.append('alt', alt);
    var response = await fetch('/admin/content-image-upload/' + kind + '/', {
      method: 'POST',
      headers: { 'X-CSRFToken': csrfToken() },
      body: data,
    });
    var payload = await response.json();
    if (!response.ok) throw new Error(payload.message || '图片上传失败。');
    return payload;
  }

  function insertUploadedImage(quill, payload) {
    var range = quill.getSelection(true);
    quill.insertEmbed(range.index, 'image', payload.url, 'user');
    var image = quill.root.querySelector('img[src="' + CSS.escape(payload.url) + '"]:last-of-type');
    if (image) image.setAttribute('alt', payload.alt || '');
    quill.setSelection(range.index + 1, 0);
  }

  function setupRichText(source) {
    var editor = document.createElement('div');
    editor.className = 'richtext-editor';
    source.insertAdjacentElement('afterend', editor);

    var tableModuleName = null;
    if (window.TableUp && window.TableUp.TableUp) {
      tableModuleName = window.TableUp.TableUp.moduleName || 'table-up';
      Quill.register('modules/' + tableModuleName, window.TableUp.TableUp, true);
    }

    var toolbar = [
      [{ header: [2, 3, 4, false] }],
      ['bold', 'italic', 'blockquote'],
      [{ list: 'ordered' }, { list: 'bullet' }],
      ['link', 'image'],
      ['clean'],
    ];
    if (tableModuleName) {
      var tableControl = {};
      tableControl[window.TableUp.TableUp.toolName || tableModuleName] = [];
      toolbar.splice(4, 0, [tableControl]);
    }

    var modules = {
      toolbar: {
        container: toolbar,
        handlers: {
          image: function () {
            var alt = window.prompt('请输入图片替代文本；装饰图片请留空。');
            if (alt === null) return;
            var input = document.createElement('input');
            input.type = 'file';
            input.accept = '.jpg,.jpeg,.png,.webp';
            input.addEventListener('change', async function () {
              if (!input.files[0]) return;
              try {
                insertUploadedImage(quill, await uploadImage(input.files[0], source.dataset.uploadKind, alt));
              } catch (error) {
                window.alert(error.message);
              }
            });
            input.click();
          },
        },
      },
    };
    if (tableModuleName) {
      modules[tableModuleName] = {
        customSelect: window.TableUp.defaultCustomSelect,
        customBtn: true,
        modules: [
          { module: window.TableUp.TableSelection },
          { module: window.TableUp.TableMenuContextmenu },
        ],
      };
    }

    var quill = new Quill(editor, { theme: 'snow', modules: modules });
    quill.clipboard.dangerouslyPasteHTML(source.value || '');
    quill.on('text-change', function () { source.value = quill.root.innerHTML; });

    quill.root.addEventListener('paste', function (event) {
      var items = Array.from(event.clipboardData?.items || []);
      var imageItem = items.find(function (item) { return item.type.startsWith('image/'); });
      if (!imageItem) return;
      event.preventDefault();
      var alt = window.prompt('请输入粘贴图片的替代文本；装饰图片请留空。');
      if (alt === null) return;
      uploadImage(imageItem.getAsFile(), source.dataset.uploadKind, alt)
        .then(function (payload) { insertUploadedImage(quill, payload); })
        .catch(function (error) { window.alert(error.message); });
    });

    source.form?.addEventListener('submit', function () {
      source.value = quill.root.innerHTML;
    });
  }

  function setupFocalPoint() {
    var xInput = document.getElementById('id_focal_x');
    var yInput = document.getElementById('id_focal_y');
    var preview = document.querySelector('[data-focal-preview]');
    if (!xInput || !yInput || !preview) return;
    var marker = preview.querySelector('.focal-point-marker');
    function updateMarker() {
      marker.style.left = (Number(xInput.value || .5) * 100) + '%';
      marker.style.top = (Number(yInput.value || .5) * 100) + '%';
    }
    preview.addEventListener('click', function (event) {
      var rect = preview.getBoundingClientRect();
      xInput.value = Math.max(0, Math.min(1, (event.clientX - rect.left) / rect.width)).toFixed(4);
      yInput.value = Math.max(0, Math.min(1, (event.clientY - rect.top) / rect.height)).toFixed(4);
      updateMarker();
    });
    updateMarker();
  }

  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('textarea.richtext-source').forEach(setupRichText);
    setupFocalPoint();
  });
}());
