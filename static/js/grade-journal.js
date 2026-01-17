const GradeJournal = {
    init: function() {
        const table = document.querySelector('.grade-journal-table');
        if (!table) return;

        table.addEventListener('input', (e) => {
            if (e.target.classList.contains('grade-input')) {
                this.handleInput(e.target);
            }
        });

        const exportBtn = document.querySelector('#export-csv');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => this.exportToCSV(table));
        }
    },

    handleInput: function(input) {
        let value = input.value.trim();
        if (value === '') {
            input.classList.remove('grade-low');
            return;
        }

        const grade = parseInt(value);
        if (isNaN(grade) || grade < 1 || grade > 10) {
            input.value = '';
            input.classList.remove('grade-low');
            return;
        }

        if (grade === 1 || grade === 2) {
            input.classList.add('grade-low');
        } else {
            input.classList.remove('grade-low');
        }

        this.updateAverages(input.closest('tr'));
    },

    updateAverages: function(row) {
        const inputs = row.querySelectorAll('.grade-input');
        let sum = 0;
        let count = 0;
        inputs.forEach(input => {
            const val = parseInt(input.value);
            if (!isNaN(val)) {
                sum += val;
                count++;
            }
        });

        const avgCell = row.querySelector('.average-cell');
        if (avgCell && count > 0) {
            avgCell.textContent = (sum / count).toFixed(2);
        }
    },

    exportToCSV: function(table) {
        let csv = [];
        const rows = table.querySelectorAll('tr');
        
        for (let i = 0; i < rows.length; i++) {
            let row = [], cols = rows[i].querySelectorAll('td, th');
            
            for (let j = 0; j < cols.length; j++) {
                let data = cols[j].querySelector('input') ? cols[j].querySelector('input').value : cols[j].innerText;
                row.push('"' + data + '"');
            }
            csv.push(row.join(','));
        }

        const csvContent = "data:text/csv;charset=utf-8," + csv.join("\n");
        const encodedUri = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", "grade_journal.csv");
        document.body.appendChild(link);
        link.click();
    }
};

document.addEventListener('DOMContentLoaded', () => GradeJournal.init());
