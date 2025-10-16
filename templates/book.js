document.addEventListener("DOMContentLoaded", function () {
    const urlParams = new URLSearchParams(window.location.search);
    const bookTitle = urlParams.get("title");

    if (!bookTitle) {
        console.error("🚨 Xatolik: URL da title parametri yo'q!");
        return;
    }

    console.log("🔎 Qidirilayotgan kitob:", bookTitle);

    fetch(`http://127.0.0.1:5000/book?title=${encodeURIComponent(bookTitle)}`)
        .then(response => {
            if (!response.ok) {
                throw new Error("❌ Serverdan noto‘g‘ri javob!");
            }
            return response.json();
        })
        .then(book => {
            console.log("📚 API'dan kelgan ma'lumot:", book);

            if (!book.cover || book.cover.trim() === "") {
                console.warn("⚠ Muqova yo‘q! Default rasm ishlatilmoqda.");
                book.cover = "images/default-book.jpg"; // ⚠ Default muqova
            }

            document.getElementById("bookTitle").textContent = book.title || "Noma'lum nom";
            document.getElementById("bookCover").src = book.cover;
            document.getElementById("bookUploader").textContent = book.username || "Noma'lum foydalanuvchi";
            document.getElementById("downloadBtn").href = `http://127.0.0.1:5000/uploads/${book.filename}`;
        })
        .catch(error => {
            console.error("🚨 Xatolik:", error);
            document.getElementById("bookDetails").innerHTML = "<p class='text-danger'>❌ Ma'lumotlarni yuklashda xatolik yuz berdi.</p>";
        });
});
