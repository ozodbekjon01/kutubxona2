document.addEventListener("DOMContentLoaded", function () {
    const bookList = document.getElementById("book-list");
    const searchInput = document.getElementById("searchInput");
    const searchResults = document.getElementById("searchResults");

    if (!bookList) {
        console.error("❌ Xatolik: book-list elementi topilmadi!");
        return;
    }


    

    // 📚 Kitoblarni yuklash funksiyasi
    function fetchBooks() {
    console.log("🔄 Kitoblar yuklanmoqda...");
    searchResults.innerHTML = ""; // Qidiruv natijalarini tozalash

    fetch("http://127.0.0.1:5000/books")
        .then(response => response.json())
        .then(books => {
            bookList.innerHTML = "";
            books.reverse().forEach(book => { // Kitoblar ro‘yxatini teskari tartibda chiqarish
                if (!book.filename) {
                    console.error("🚨 Xato: book.filename undefined:", book);
                    return;
                }

                // book.html sahifasiga kerakli ma'lumotlarni o'tkazish
                let bookUrl = `book.html?title=${encodeURIComponent(book.title)}&cover=${encodeURIComponent(book.cover)}&uploader=${encodeURIComponent(book.username)}&filename=${encodeURIComponent(book.filename)}`;

                let bookItem = `
                    <div class="col-6 col-sm-4 col-md-3 col-lg-2 col-xl-2 custom-col">
                        <div class="card mb-4 shadow-sm" onclick="window.location.href='${bookUrl}'" style="cursor: pointer;">
                            <img src="${book.cover}" class="card-img-top custom-img" alt="${book.title}">
                            <img src="${book.cover}" alt="${book.title}" class="card-img-top custom-img" loading="lazy">

                        <div class="card-body">
                            <h5 class="card-title">${book.title}</h5>
                            <p class="card-text"><strong>Yuklagan:</strong> ${book.username}</p>
                        </div>
                        </div>
                    </div>
                `;

                bookList.innerHTML += bookItem;
            });
        })
        .catch(error => console.error("🚨 Xatolik:", error));
}

    fetchBooks(); // Sahifa yuklanganda kitoblarni yuklash

    // 🔍 Qidiruv funksiyasi
    searchInput.addEventListener("keyup", function () {
        let query = searchInput.value.trim();
        
        if (!query) {
            searchResults.innerHTML = ""; // Agar input bo‘sh bo‘lsa, natijalarni tozalaymiz
            fetchBooks(); // Asosiy kitoblar ro‘yxatini qayta yuklaymiz
            return;
        }

        console.log("🔎 Qidiruv so‘rovi:", query);

        fetch(`http://127.0.0.1:5000/search?query=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                searchResults.innerHTML = ""; // Oldingi natijalarni o‘chiramiz

                if (data.length === 0) {
                    searchResults.innerHTML = "<p class='text-center text-warning'>⚠ Natijalar topilmadi!</p>";
                    return;
                }

                data.forEach(book => {
                    let bookUrl = `book.html?title=${encodeURIComponent(book.title)}&cover=${encodeURIComponent(book.cover)}&uploader=${encodeURIComponent(book.username)}&filename=${encodeURIComponent(book.filename)}`;

                    let resultItem = `
                        <div class="d-flex justify-content-center" onclick="window.location.href='${bookUrl}'" style="cursor: pointer;">
    <div class="card p-2 mb-2 border-0 shadow-sm" style="max-width: 600px;height:100px; width: 100%;">
        <div class="d-flex align-items-center">
            <!-- Muqova -->
            <img src="${book.cover}" alt="Muqova" class="rounded" style="width: 60px; height: 80px; object-fit: cover;">

            <!-- Kitob haqida ma'lumot -->
            <div class="ms-3 flex-grow-1">
                <h6 class="mb-1 text-truncate" style="max-width: 350px;">${book.title}</h6>
                <p class="mb-0 text-muted" style="font-size: 14px;"><strong>Yuklagan:</strong> ${book.username}</p>
            </div>

            <!-- Yuklab olish tugmasi -->
            <div>
                <a href="book.html?title=${encodeURIComponent(book.title)}" class="btn btn-sm btn-info mt-1">Kitobni ko‘rish</a>
            </div>
        </div>
    </div>
</div>


                    `;

                    searchResults.innerHTML += resultItem;
                });
            })
            .catch(error => {
                console.error("Xatolik:", error);
                searchResults.innerHTML = "<p class='text-danger'>❌ Xatolik yuz berdi!</p>";
            });
    });
});


