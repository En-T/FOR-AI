const TransferBox = {
    init: function() {
        const containers = document.querySelectorAll('.transfer-box-container');
        containers.forEach(container => {
            this.setupContainer(container);
        });
    },

    setupContainer: function(container) {
        const leftList = container.querySelector('.list-unassigned');
        const rightLists = container.querySelectorAll('.list-group');
        const moveRightBtn = container.querySelector('.btn-move-right');
        const moveLeftBtn = container.querySelector('.btn-move-left');

        container.addEventListener('click', (e) => {
            const item = e.target.closest('.transfer-box-item');
            if (item) {
                item.classList.toggle('selected');
            }
        });

        if (moveRightBtn) {
            moveRightBtn.addEventListener('click', () => {
                const selectedItems = leftList.querySelectorAll('.transfer-box-item.selected');
                const targetGroup = container.querySelector('input[name="target-group"]:checked')?.value || 0;
                const targetList = rightLists[targetGroup] || rightLists[0];
                
                selectedItems.forEach(item => {
                    item.classList.remove('selected');
                    targetList.appendChild(item);
                    this.updateHiddenInput(item, targetGroup);
                });
            });
        }

        if (moveLeftBtn) {
            moveLeftBtn.addEventListener('click', () => {
                rightLists.forEach(list => {
                    const selectedItems = list.querySelectorAll('.transfer-box-item.selected');
                    selectedItems.forEach(item => {
                        item.classList.remove('selected');
                        leftList.appendChild(item);
                        this.updateHiddenInput(item, '');
                    });
                });
            });
        }
    },

    updateHiddenInput: function(item, groupId) {
        const studentId = item.dataset.id;
        let input = document.querySelector(`input[name="student_${studentId}_group"]`);
        if (!input) {
            input = document.createElement('input');
            input.type = 'hidden';
            input.name = `student_${studentId}_group`;
            item.appendChild(input);
        }
        input.value = groupId;
    }
};

document.addEventListener('DOMContentLoaded', () => TransferBox.init());
