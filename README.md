# Bahasa Indonesia Language Processing

Aplikasi ini dibuat untuk membantu membuat kamus kata-kata _alay_ yang ditemukan di media sosial sehingga lebih mudah untuk diproses dan diolah lebih lanjut. Ke depannya, aplikasi ini akan dihubungkan dengan API untuk melakukan pengecekan kata-kata baku yang sudah ada dalam Kamus Besar Bahasa Indonesia.

Untuk menjalankan aplikasi ini secara lokal, silakan _clone_ repositori ini dengan,

    git clone https://github.com/tentangdata/bilp-heroku.git

lalu install `virtualenv`  dengan menggunakan _package manager Python_

    sudo pip install virtualenv

atau dengan cara apapun yang Anda suka -- mungkin Anda lebih senang mengompilasi semuanya sendiri?

Buatlah folder `venv` pada repositori yang telah Anda _clone_ dengan perintah

    virtualenv venv

Kemudian, Anda dapat menginstalasi semua _dependency_ yang dibutuhkan dengan menggunakan perintah

    pip install -r requirements.txt

Saat ini, struktur basis data yang akan dikembangkan dapat dilihat di gambar di bawah ini.

![ER-Diagram](bilp-er.png)

Selamat bereksperimen!
