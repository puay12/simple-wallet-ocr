module.exports = {
  apps: [
    {
      name: "simple-wallet-ocr",
      cmd: "gunicorn --bind 0.0.0.0:8080 wsgi:app",
      interpreter: "python3",
      autorestart: true,
      watch: true,
      ignore_watch: ["images"],
    },
  ],
};
