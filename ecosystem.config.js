module.exports = {
  apps: [
    {
      name: "simple-wallet-ocr",
      cmd: "gunicorn --bind 0.0.0.0:8080 wsgi:app",
      autorestart: true,
      watch: true,
      ignore_watch: ["images"],
    },
  ],
};
