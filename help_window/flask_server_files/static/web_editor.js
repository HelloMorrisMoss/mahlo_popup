let currentArticlePath = null;
let currentArticleData = [];
let previousArticlePath = null;
let expandedFolders = new Set(["Root"]); // Root expanded by default

async function refreshArticleList() {
    const response = await fetch('/api/structure');
    const tree = await response.json();
    const list = document.getElementById('article-list');
    list.innerHTML = '';

    // Sort children: folders first, then articles
    const sortedChildren = tree.children.sort((a, b) => {
        if (a.type !== b.type) return a.type === 'folder' ? -1 : 1;
        return a.name.localeCompare(b.name);
    });

    sortedChildren.forEach(child => {
        list.appendChild(renderTreeNode(child));
    });
}

function renderTreeNode(node) {
    const div = document.createElement('div');
    if (node.type === 'folder') {
        const isExpanded = expandedFolders.has(node.path) || node.name === "Root";
        const header = document.createElement('div');
        header.className = 'folder-item' + (node.is_media ? ' media-folder' : '');
        header.dataset.path = node.path;

        let label = node.name;
        if (node.is_media) {
            label += ` (${node.item_count || 0})`;
        }

        const toggleIcon = isExpanded ? '▼' : '▶';
        const folderIcon = node.is_media ? '📁' : (isExpanded ? '📂' : '📁');

        header.innerHTML = `<span class="article-icon" style="cursor:pointer; width: 10px; display: inline-block;">${node.is_media ? '' : toggleIcon}</span> <span class="article-icon">${folderIcon}</span> ${label}`;
        
        header.onclick = (e) => {
            e.stopPropagation();
            if (e.target.innerText === '▶' || e.target.innerText === '▼' || (!node.is_media && e.detail > 1)) {
                toggleFolder(node.path);
                return;
            }

            if (node.is_media) {
                showMediaBrowser(node.path);
            } else {
                showFolderOptions(node);
            }
        };
        div.appendChild(header);

        const content = document.createElement('div');
        content.className = 'folder-content';
        content.style.display = isExpanded ? 'block' : 'none';

        const children = node.children || [];
        children.sort((a, b) => {
            if (a.type !== b.type) return a.type === 'folder' ? -1 : 1;
            return a.name.localeCompare(b.name);
        });

        children.forEach(child => {
            content.appendChild(renderTreeNode(child));
        });
        div.appendChild(content);
    } else {
        const item = document.createElement('div');
        item.className = 'article-item';
        item.dataset.path = node.path;
        if (node.path === currentArticlePath) item.classList.add('selected');
        item.innerHTML = `<span class="article-icon">📄</span> ${node.name}`;
        item.onclick = (e) => {
            e.stopPropagation();
            loadArticle(node.path, node.name);
        };
        div.appendChild(item);
    }
    return div;
}

function toggleFolder(path) {
    if (expandedFolders.has(path)) {
        expandedFolders.delete(path);
    } else {
        expandedFolders.add(path);
    }
    // We don't need to fetch from server just to toggle UI, but refreshArticleList does that.
    // For now, let's just re-render from local state if we had it, but refresh is safer.
    refreshArticleList();
}

async function loadArticle(path, title) {
    if (currentArticlePath) previousArticlePath = currentArticlePath;
    currentArticlePath = path;
    const response = await fetch(`/api/article?path=${encodeURIComponent(path)}`);
    currentArticleData = await response.json();

    document.getElementById('current-article-name').textContent = title;
    document.getElementById('editor-actions').style.display = 'flex';
    document.getElementById('add-block-toolbar').style.display = 'flex';

    // Refresh the add block toolbar
    renderAddBlockToolbar();

    // Highlight in list
    document.querySelectorAll('#article-list .article-item').forEach(item => {
        item.classList.toggle('selected', item.dataset.path === path);
    });

    renderEditor();
    renderPreview();
}

function renderAddBlockToolbar() {
    const toolbar = document.getElementById('add-block-toolbar');
    toolbar.innerHTML = '';
    const types = ["title", "header", "subheader", "paragraph", "image", "video", "link", "separator"];
    types.forEach(t => {
        const btn = document.createElement('button');
        btn.textContent = t.charAt(0).toUpperCase() + t.slice(1);
        btn.onclick = () => addSpecificBlock(t);
        toolbar.appendChild(btn);
    });
}

function addSpecificBlock(type) {
    if (type === 'title' && currentArticleData.some(b => b.type === 'title')) {
        alert("Article already has a title block.");
        return;
    }
    const newBlock = {type: type, content: ''};
    if (type === 'link') newBlock.target = '';
    if (type === 'title') {
        // Titles must be at the top
        currentArticleData.unshift(newBlock);
    } else {
        currentArticleData.push(newBlock);
    }
    renderEditor();
    renderPreview();
}

function renderEditor() {
    const list = document.getElementById('block-list');
    list.innerHTML = '';

    currentArticleData.forEach((block, index) => {
        const div = document.createElement('div');
        div.className = 'block-edit';

        const typeLabel = document.createElement('div');
        typeLabel.className = 'block-type-label';
        typeLabel.textContent = block.type;
        div.appendChild(typeLabel);

        const controls = document.createElement('div');
        controls.className = 'block-controls';
        controls.innerHTML = `
            <button onclick="moveBlock(${index}, -1)">↑</button>
            <button onclick="moveBlock(${index}, 1)">↓</button>
            <button class="danger" onclick="removeBlock(${index})">Delete</button>
        `;
        div.appendChild(controls);

        if (block.type === 'image' || block.type === 'video') {
            const input = document.createElement('input');
            input.type = 'text';
            input.value = block.content;
            input.placeholder = 'Path to media...';
            input.style.marginBottom = '5px';
            input.oninput = (e) => {
                block.content = e.target.value;
                renderPreview();
            };
            div.appendChild(input);

            const uploadBtn = document.createElement('button');
            uploadBtn.textContent = 'Upload Media...';
            uploadBtn.onclick = () => triggerUpload(index);
            div.appendChild(uploadBtn);
        } else if (block.type === 'link') {
            const input = document.createElement('input');
            input.type = 'text';
            input.value = block.content;
            input.placeholder = 'Link text...';
            input.style.marginBottom = '5px';
            input.oninput = (e) => {
                block.content = e.target.value;
                renderPreview();
            };
            div.appendChild(input);

            const targetContainer = document.createElement('div');
            targetContainer.style.display = 'flex';
            targetContainer.style.gap = '5px';

            const targetInput = document.createElement('input');
            targetInput.type = 'text';
            targetInput.value = block.target;
            targetInput.placeholder = 'Target article path (relative)...';
            targetInput.style.flex = '1';
            targetInput.oninput = (e) => {
                block.target = e.target.value;
                renderPreview();
            };
            targetContainer.appendChild(targetInput);

            const browseBtn = document.createElement('button');
            browseBtn.textContent = 'Browse...';
            browseBtn.onclick = () => showArticleSelector(index);
            targetContainer.appendChild(browseBtn);

            div.appendChild(targetContainer);
        } else if (block.type === 'separator') {
            const label = document.createElement('div');
            label.textContent = '(Visual Separator)';
            label.style.fontStyle = 'italic';
            label.style.color = '#888';
            div.appendChild(label);
        } else {
            const textarea = document.createElement('textarea');
            textarea.value = block.content;
            textarea.rows = block.type === 'paragraph' ? 4 : 1;
            textarea.oninput = (e) => {
                block.content = e.target.value;
                renderPreview();
            };
            div.appendChild(textarea);
        }

        list.appendChild(div);
    });
}

function renderPreview() {
    const preview = document.getElementById('preview-content');
    preview.innerHTML = '';

    currentArticleData.forEach(block => {
        let el;
        switch (block.type) {
            case 'title':
                // Title is mandatory but we don't always render it in ArticleViewer
                // but for preview it's good to see.
                el = document.createElement('h1');
                el.className = 'preview-title';
                el.textContent = block.content;
                el.style.display = 'block';
                break;
            case 'header':
                el = document.createElement('h2');
                el.className = 'preview-header';
                el.textContent = block.content;
                break;
            case 'subheader':
                el = document.createElement('h3');
                el.className = 'preview-subheader';
                el.textContent = block.content;
                break;
            case 'paragraph':
                el = document.createElement('p');
                el.className = 'preview-paragraph';
                el.textContent = block.content;
                break;
            case 'image':
                el = document.createElement('img');
                el.className = 'preview-image';
                // Remove help_window/help_content from the path if it's there
                let src = block.content.replace('help_window/help_content/', '');
                el.src = `/media/${src}`;
                break;
            case 'video':
                el = document.createElement('div');
                el.className = 'preview-video';
                el.textContent = `[Video Player: ${block.content}]`;
                break;
            case 'link':
                el = document.createElement('a');
                el.className = 'preview-link';
                el.textContent = block.content;
                el.href = '#';
                break;
            case 'separator':
                el = document.createElement('hr');
                el.style.margin = '20px 0';
                el.style.border = '0';
                el.style.borderTop = '1px solid #eee';
                break;
        }
        if (el) preview.appendChild(el);
    });
}

function cancelEdit() {
    if (confirm("Are you sure you want to cancel? All unsaved changes will be lost.")) {
        if (currentArticlePath) {
            // Reload original
            loadArticle(currentArticlePath, document.getElementById('current-article-name').textContent);
        }
    }
}

async function consolidateMedia() {
    try {
        const response = await fetch('/api/consolidate', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({path: currentArticlePath, content: currentArticleData})
        });
        const result = await response.json();
        if (result.status === 'success') {
            if (result.changed) {
                currentArticleData = result.content;
                renderEditor();
                renderPreview();
                alert("Media consolidated successfully.");
            } else {
                alert("All media already consolidated.");
            }
        } else {
            alert("Error consolidating media: " + result.error);
        }
    } catch (e) {
        alert("Network error while consolidating media.");
    }
}

/* Modal and Dialogs */

function esc(str) {
    if (!str) return "";
    return JSON.stringify(str).replace(/"/g, '&quot;');
}

function showModal(title, bodyHtml, footerHtml) {
    const modal = document.getElementById('modal-overlay');
    const content = document.getElementById('modal-content');

    content.innerHTML = `
        <div class="modal-header">
            <h2 style="margin:0">${title}</h2>
            <button onclick="hideModal()">&times;</button>
        </div>
        <div class="modal-body">${bodyHtml}</div>
        <div class="modal-footer">${footerHtml || '<button onclick="hideModal()">Close</button>'}</div>
    `;

    modal.style.display = 'flex';
}

function hideModal() {
    document.getElementById('modal-overlay').style.display = 'none';

    // HLP-036.4: Selection reversion logic
    if (!currentArticlePath) {
        // Find help_for_help or first available
        findAndLoadDefaultArticle();
    }
}

async function findAndLoadDefaultArticle() {
    const response = await fetch('/api/articles');
    const articles = await response.json();
    let target = articles.find(a => a.file_path.includes('help_for_help.json'));
    if (!target && articles.length > 0) target = articles[0];

    if (target) {
        loadArticle(target.file_path, target.title);
    }
}

async function showMediaBrowser(path) {
    const response = await fetch(`/api/media_list?path=${encodeURIComponent(path)}`);
    const files = await response.json();

    let body = '<div class="media-grid">';
    files.forEach(file => {
        const isImage = /\.(jpg|jpeg|png|gif|bmp|webp)$/i.test(file.name);
        body += `
            <div class="media-item" onclick="previewMedia(${esc(file.url)}, ${esc(file.name)})">
                ${isImage ? `<img src="${file.url}">` : '<div style="height:60px; display:flex; align-items:center; justify-content:center; font-size:24px;">📄</div>'}
                <div>${file.name}</div>
            </div>
        `;
    });
    body += '</div>';

    showModal('Media Browser', body, '<button onclick="hideModal()">Close</button>');
}

function previewMedia(url, name) {
    const isImage = /\.(jpg|jpeg|png|gif|bmp|webp)$/i.test(name);
    let html = '';
    if (isImage) {
        html = `<img src="${url}" style="max-width:100%; border: 1px solid #ccc;">`;
    } else {
        html = `<p>Preview not available for this file type: ${name}</p>`;
    }

    // We can just alert or show another modal, but let's just alert for now or replace body
    showModal(`Preview: ${name}`, html, '<button onclick="hideModal()">Back</button>');
}

function showFolderOptions(folder) {
    const body = `
        <p>Folder: <strong>${folder.name}</strong></p>
        <div style="display: flex; flex-direction: column; gap: 10px;">
            <button onclick="renameFolderPrompt(${esc(folder.path)})">Rename Folder</button>
            <button onclick="moveFolderPrompt(${esc(folder.path)})">Move Folder</button>
            <button class="danger" onclick="deleteFolderPrompt(${esc(folder.path)})">Delete Folder</button>
            <button onclick="createNewFolderPrompt(${esc(folder.path)})">Create New Subfolder</button>
        </div>
    `;
    showModal('Folder Options', body);
}

async function moveFolderPrompt(path) {
    // Scan structure to get folders
    const response = await fetch('/api/structure');
    const tree = await response.json();

    let folders = [];

    function collectFolders(node) {
        if (node.type === 'folder' && !node.is_media && node.path !== path && !node.path.startsWith(path + '/')) {
            folders.push(node);
            node.children.forEach(collectFolders);
        }
    }

    collectFolders(tree);

    let body = '<p>Select target parent folder:</p><div style="max-height: 400px; overflow-y: auto;">';
    folders.forEach(f => {
        body += `<div class="article-item" onclick="confirmMoveFolder(${esc(path)}, ${esc(f.path)})">${f.name} (${f.path})</div>`;
    });
    body += '</div>';

    showModal('Move Folder', body);
}

async function confirmMoveFolder(oldPath, newParentPath) {
    const response = await fetch('/api/move', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({old_path: oldPath, new_parent: newParentPath})
    });
    if (response.ok) {
        hideModal();
        refreshArticleList();
    } else {
        const err = await response.json();
        alert("Error moving folder: " + err.error);
    }
}

async function renameFolderPrompt(path) {
    const newName = prompt("Enter new name:");
    if (!newName) return;

    const response = await fetch('/api/rename', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({path, new_name: newName})
    });
    if (response.ok) {
        hideModal();
        refreshArticleList();
    } else {
        const err = await response.json();
        alert("Error renaming: " + err.error);
    }
}

async function deleteFolderPrompt(path) {
    if (confirm("Are you sure you want to delete this folder and all its contents?")) {
        const response = await fetch('/api/delete', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({path})
        });
        if (response.ok) {
            hideModal();
            refreshArticleList();
        } else {
            const err = await response.json();
            alert("Error deleting: " + err.error);
        }
    }
}

async function createNewFolderPrompt(parentPath) {
    const name = prompt("Enter folder name:");
    if (!name) return;

    const response = await fetch('/api/create_folder', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({parent_path: parentPath, name})
    });
    if (response.ok) {
        hideModal();
        refreshArticleList();
    } else {
        const err = await response.json();
        alert("Error creating folder: " + err.error);
    }
}

async function moveArticle() {
    if (!currentArticlePath) return;

    // Scan structure to get folders
    const response = await fetch('/api/structure');
    const tree = await response.json();

    let folders = [];

    function collectFolders(node) {
        if (node.type === 'folder' && !node.is_media) {
            folders.push(node);
            node.children.forEach(collectFolders);
        }
    }

    collectFolders(tree);

    let body = '<p>Select target folder:</p><div style="max-height: 400px; overflow-y: auto;">';
    folders.forEach(f => {
        body += `<div class="article-item" onclick="confirmMoveArticle(${esc(f.path)})">${f.name} (${f.path})</div>`;
    });
    body += '</div>';

    showModal('Move Article', body);
}

async function confirmMoveArticle(newParentPath) {
    const response = await fetch('/api/move', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({old_path: currentArticlePath, new_parent: newParentPath})
    });
    if (response.ok) {
        const result = await response.json();
        hideModal();
        currentArticlePath = result.new_path;
        await refreshArticleList();
        loadArticle(currentArticlePath, document.getElementById('current-article-name').textContent);
    } else {
        const err = await response.json();
        alert("Error moving: " + err.error);
    }
}

async function showArticleSelector(blockIndex) {
    const response = await fetch('/api/articles');
    const articles = await response.json();

    let body = '<div style="max-height: 400px; overflow-y: auto;">';
    articles.forEach(a => {
        body += `<div class="article-item" onclick="selectArticleForLink(${blockIndex}, ${esc(a.file_path)})">${a.title} (${a.section || 'Root'})</div>`;
    });
    body += '</div>';

    showModal('Select Target Article', body);
}

function selectArticleForLink(blockIndex, path) {
    // Convert absolute path to relative if possible
    // In our case, the help system expects relative paths from project root or relative to article
    // The existing file_manager logic handles some of this.
    // Let's just use the path as is, and maybe refine later.
    currentArticleData[blockIndex].target = path;
    hideModal();
    renderEditor();
    renderPreview();
}

function removeBlock(index) {
    if (currentArticleData[index].type === 'title') {
        alert("Cannot delete mandatory title block.");
        return;
    }
    if (confirm("Are you sure you want to delete this block?")) {
        currentArticleData.splice(index, 1);
        renderEditor();
        renderPreview();
    }
}

function moveBlock(index, delta) {
    const newIndex = index + delta;
    if (newIndex < 0 || newIndex >= currentArticleData.length) return;

    // Title block must stay at index 0
    if (index === 0 || newIndex === 0) return;

    const temp = currentArticleData[index];
    currentArticleData[index] = currentArticleData[newIndex];
    currentArticleData[newIndex] = temp;
    renderEditor();
    renderPreview();
}

async function saveCurrentArticle() {
    try {
        const response = await fetch('/api/article', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({path: currentArticlePath, content: currentArticleData})
        });
        if (response.ok) {
            alert("Article saved successfully!");
            refreshArticleList();
        } else {
            const err = await response.json();
            alert("Error saving article: " + err.error);
        }
    } catch (e) {
        alert("Network error while saving article.");
    }
}

function triggerUpload(blockIndex) {
    const input = document.createElement('input');
    input.type = 'file';
    input.onchange = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);
        formData.append('article_path', currentArticlePath);

        try {
            const response = await fetch('/api/upload_media', {
                method: 'POST',
                body: formData
            });
            const result = await response.json();
            if (result.status === 'success') {
                currentArticleData[blockIndex].content = result.path;
                renderEditor();
                renderPreview();
            } else {
                alert("Upload failed: " + result.error);
            }
        } catch (e) {
            alert("Network error during upload.");
        }
    };
    input.click();
}

async function createNewArticle() {
    const title = prompt("Enter article title:");
    if (!title) return;

    const section = prompt("Enter section (optional, e.g. 'CategoryName'):", "");

    try {
        const response = await fetch('/api/create_article', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({title, section})
        });
        const result = await response.json();
        if (response.ok) {
            await refreshArticleList();
            loadArticle(result.file_path, title);
        } else {
            alert("Error creating article: " + result.error);
        }
    } catch (e) {
        alert("Network error while creating article.");
    }
}

// Initial load
async function init() {
    await refreshArticleList();

    // Check if we should show the publishing button
    try {
        const response = await fetch('/api/config');
        const config = await response.json();
        if (config.is_server) {
            document.getElementById('publishing-btn').style.display = 'inline-block';
        }
    } catch (e) {
        console.error("Error fetching config:", e);
    }
}

init();
