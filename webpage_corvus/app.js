// Corvus Documentation Website Interactive App Engine

document.addEventListener('DOMContentLoaded', () => {
    // 1. Copy Code Snippet Functionality
    const codeBlocks = document.querySelectorAll('pre');
    codeBlocks.forEach((block) => {
        const wrapper = document.createElement('div');
        wrapper.className = 'code-wrapper';
        block.parentNode.insertBefore(wrapper, block);
        wrapper.appendChild(block);

        const copyBtn = document.createElement('button');
        copyBtn.className = 'copy-btn';
        copyBtn.innerText = 'Copy';
        wrapper.appendChild(copyBtn);

        copyBtn.addEventListener('click', () => {
            const codeText = block.innerText;
            navigator.clipboard.writeText(codeText).then(() => {
                copyBtn.innerText = 'Copied!';
                copyBtn.style.color = '#4ade80';
                setTimeout(() => {
                    copyBtn.innerText = 'Copy';
                    copyBtn.style.color = '';
                }, 2000);
            });
        });
    });

    // 2. Interactive Version Tutorial Tabs
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabBtns.forEach((btn) => {
        btn.addEventListener('click', () => {
            const targetTab = btn.getAttribute('data-tab');

            tabBtns.forEach((b) => b.classList.remove('active'));
            tabContents.forEach((c) => c.classList.remove('active'));

            btn.classList.add('active');
            const activeContent = document.getElementById(targetTab);
            if (activeContent) {
                activeContent.classList.add('active');
            }
        });
    });

    // 3. Real-time Documentation Search
    const searchInput = document.getElementById('doc-search');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase().trim();
            const sections = document.querySelectorAll('.doc-section');

            sections.forEach((sec) => {
                const text = sec.innerText.toLowerCase();
                if (query === '' || text.includes(query)) {
                    sec.style.display = 'block';
                } else {
                    sec.style.display = 'none';
                }
            });
        });
    }

    // 4. Active Sidebar Link Tracking on Scroll
    const observerOptions = {
        root: null,
        rootMargin: '-20% 0px -70% 0px',
        threshold: 0
    };

    const navLinks = document.querySelectorAll('.sidebar-nav a');
    const sections = document.querySelectorAll('.doc-section');

    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                const id = entry.target.getAttribute('id');
                navLinks.forEach((link) => {
                    if (link.getAttribute('href') === `#${id}`) {
                        link.classList.add('active');
                    } else {
                        link.classList.remove('active');
                    }
                });
            }
        });
    }, observerOptions);

    sections.forEach((sec) => observer.observe(sec));
});
