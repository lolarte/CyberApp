document.addEventListener("DOMContentLoaded", function () {
    let textareas = document.querySelectorAll(".quill-editor");

    textareas.forEach(function (textarea) {
        let wrapper = document.createElement("div");
        wrapper.classList.add("quill-wrapper");

        let quillContainer = document.createElement("div");
        quillContainer.classList.add("quill-container");

        // Insert wrapper before the textarea
        textarea.parentNode.insertBefore(wrapper, textarea);
        wrapper.appendChild(quillContainer);
        textarea.style.display = "none";  // ✅ Hide original textarea

        // ✅ Register Image Resizing
        if (window.Quill && window.QuillResizeImage) {
            Quill.register("modules/resize", window.QuillResizeImage);
            console.log("✅ Image Resize module loaded successfully!");
        } else {
            console.error("❌ Image Resize module not loaded.");
        }


        // ✅ Define Custom "View Source" Button
        function toggleSourceView(quill) {
            let editor = quill.root;
            let sourceMode = editor.getAttribute("data-source-mode");

            if (!sourceMode || sourceMode === "off") {
                let pre = document.createElement("textarea");
                pre.setAttribute("id", "quill-source-view");
                pre.style.border = "1px solid #ccc";
                pre.style.padding = "10px";
                pre.style.width = "100%";
                pre.style.height = "300px";
                pre.style.overflow = "auto";
                pre.value = editor.innerHTML;

                editor.parentNode.replaceChild(pre, editor);
                pre.setAttribute("data-source-mode", "on");
            } else {
                let pre = document.getElementById("quill-source-view");
                let div = document.createElement("div");
                div.innerHTML = pre.value;
                div.setAttribute("class", "ql-editor");
                div.setAttribute("contenteditable", "true");

                pre.parentNode.replaceChild(div, pre);
            }
        }

        // Initialize Quill 2.0 with a custom "View Source" button
        let quill = new Quill(quillContainer, {
            theme: "snow",
            placeholder: "Type here...",
            modules: {
                toolbar: {
                    container: [
                        [{ 'header': [1, 2, false] }],
                        ['bold', 'italic', 'underline'],
                        [{ 'color': [] }, { 'background': [] }],
                        [{ 'list': 'ordered' }, { 'list': 'bullet' }, { 'indent': '-1' }, { 'indent': '+1' }],
                        ['direction', { 'align': [] }],
                        ['link', 'image', 'video', 'formula'],
                        ['table'],  // ✅ Adds Table Button
                        ['viewSource']  // ✅ Add View Source Button
                    ],
                    handlers: {
                        viewSource: function() {
                            toggleSourceView(quill);
                        }
                    }
                },
                resize: {
                    locale: {
                        center: "Center",
                    }
                },  // ✅ Enable Image Resizing
                "better-table": {  // ✅ Enable Table Module
                    operationMenu: {
                        items: {
                            unmergeCells: { text: "Unmerge Cells" }
                        }
                    },
                    clipboard: {
                        matchVisual: false
                    }
                }
            }
        });

        // ✅ Load existing content into Quill if editing an existing entry
        quill.root.innerHTML = textarea.value;

        // ✅ Sync Quill content to the textarea before form submission
        function syncQuillContent() {
            let sourceView = document.getElementById("quill-source-view");
            if (sourceView) {
                textarea.value = sourceView.value;  // ✅ Save HTML source code
            } else {
                textarea.value = quill.root.innerHTML;  // ✅ Save normal Quill content
            }
            console.log("Quill content saved:", textarea.value);  // ✅ Debugging
        }

        // ✅ Ensure content is saved when the form is submitted
        document.querySelector("form").addEventListener("submit", syncQuillContent);

        // ✅ Also save content when the user moves away from the editor
        quill.on("text-change", syncQuillContent);
    });
});
