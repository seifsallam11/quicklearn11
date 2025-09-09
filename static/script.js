// script.js
document.addEventListener('DOMContentLoaded', () => {
  const generateBtn = document.getElementById('generateBtn');
  const openTabBtn = document.getElementById('openTabBtn');
  const lessonInput = document.getElementById('lessonInput');
  const resultFrame = document.getElementById('resultFrame');

  async function sendLesson() {
    const lessonText = lessonInput.value;

    if (!lessonText.trim()) {
      alert("Please type your lesson first!");
      return;
    }

    // إظهار رسالة انتظار وتعطيل الزر
    generateBtn.disabled = true;
    generateBtn.textContent = 'Generating...';
    resultFrame.srcdoc = '<p style="text-align: center; font-family: sans-serif;">Please wait while the summary is being generated...</p>';

    try {
      // إرسال البيانات بصيغة تتوافق مع request.form في Flask
      const response = await fetch('/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `lesson_text=${encodeURIComponent(lessonText)}`
      });

      // قراءة الاستجابة كنص عادي (HTML)
      const summaryHTML = await response.text();

      if (response.ok) {
        // إذا كانت الاستجابة ناجحة (كود 200)
        resultFrame.srcdoc = summaryHTML;
        openTabBtn.style.display = 'inline-block'; // إظهار زر الفتح في تبويب جديد
      } else {
        // إذا كانت هناك استجابة خطأ من الخادم (مثال: 400، 500)
        resultFrame.srcdoc = summaryHTML;
        alert("Error: " + summaryHTML);
      }
    } catch (error) {
      // التعامل مع أخطاء الشبكة (مثل عدم الاتصال بالخادم)
      const errorMessage = `Failed to connect to the server: ${error.message}`;
      resultFrame.srcdoc = `<p style="color: red; text-align: center; font-family: sans-serif;">${errorMessage}</p>`;
      alert(errorMessage);
    } finally {
      // إعادة تفعيل الزر بغض النظر عن النتيجة
      generateBtn.disabled = false;
      generateBtn.textContent = 'Generate Summary';
    }
  }

  function openInNewTab() {
    // التأكد من وجود محتوى صالح للعرض
    if (resultFrame.srcdoc && !resultFrame.srcdoc.includes("Error")) {
      const newWindow = window.open();
      newWindow.document.write(resultFrame.srcdoc);
      newWindow.document.close();
    } else {
      alert("There is no valid summary to open.");
    }
  }

  generateBtn.addEventListener('click', sendLesson);
  openTabBtn.addEventListener('click', openInNewTab);
});