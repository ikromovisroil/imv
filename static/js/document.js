function highlightInput(inputId, targetId, defaultText) {
  const input = document.getElementById(inputId);
  const targetDivs = document.querySelectorAll(`[id='${targetId}']`);

  input.addEventListener('input', function() {
    targetDivs.forEach(div => {
      if (this.value.trim() !== "") {
        div.innerHTML = `<span style="background-color: yellow;">${this.value}</span>`;
      } else {
        div.textContent = defaultText;
      }
    });
  });
}

highlightInput('fio_id', 'fio_id_text', 'Sh.Muxamedov');


highlightInput('post_id', 'post_id_text', 'direktori');
highlightInput('namber_id', 'namber_id_text', '1');
highlightInput('rim_id', 'rim_id_text', 'I');

function highlightDate(inputId, targetId, defaultText) {
    const input = document.getElementById(inputId);
    const targetDiv = document.getElementById(targetId);

    const months = [
        "yanvarda", "fevralda", "martda", "aprelda", "mayda", "iyunda",
        "iyulda", "avgustda", "sentabrda", "oktabrda", "noyabrda", "dekabrda"
    ];

    input.addEventListener('input', function() {
        if (this.value) {
            const [year, month, day] = this.value.split('-');
            const formatted = `${year} yil ${parseInt(day)} - ${months[parseInt(month)-1]}`;
            targetDiv.innerHTML = `<span style="background-color: yellow;">${formatted}</span>`;
        } else {
            targetDiv.textContent = defaultText;
        }
    });
}

// Ishlatish
highlightDate('date_id', 'date_id_text', '2025 yil 4 - martda');

function updateSelektText() {
    // Tanlangan qiymat: org > dep > pos
    let val = $('#organization option:selected').text() || '';
    let isSelected = true;

    if ($('#department').val()) {
        val = $('#department option:selected').text();
        isSelected = true;
    }
    if ($('#position').val()) {
        val = $('#position option:selected').text();
        isSelected = true;
    }

    if(val === '' || val === 'Tanlang...') {
        val = 'Davlat byudjeti siyosati departamenti';
        isSelected = false;
    }

    // Barcha selekt_id_text spanlarini yangilaymiz
    $('span#selekt_id_text').each(function(){
        if(isSelected){
            $(this).html(`<span style="background-color: yellow;">${val}</span>`);
        } else {
            $(this).text(val); // default matn, fon yo‘q
        }
    });
}

// Change event
$('#organization, #department, #position').change(function(){
    updateSelektText();
});

// Sahifa yuklanganda oldindan tanlangan qiymat bo‘lsa
updateSelektText();