const express = require('express');
const app = express();
const port = process.env.PORT || 8080;

app.get('/', (req, res) => {
  // Generate a random hex color code
  const randomColor = Math.floor(Math.random() * 16777215).toString(16);
  // Pad with zeros in case the generated string is less than 6 characters
  const hexColor = `#${randomColor.padStart(6, '0')}`;

  const html = `
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Dynamic Color App</title>
      <style>
        body {
          background-color: ${hexColor};
          color: #333;
          font-family: Arial, sans-serif;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          height: 100vh;
          margin: 0;
          transition: background-color 0.5s ease;
        }
        .container {
          background: rgba(255, 255, 255, 0.8);
          padding: 2rem;
          border-radius: 10px;
          text-align: center;
        }
      </style>
    </head>
    <body>
      <div class="container">
        <h1>Hello from Node.js on Cloud Run!</h1>
        <h3>- Hemanshu Waghmare and Team</h3>
        <p>Current Background Color: <strong>${hexColor}</strong></p>
      </div>
    </body>
    </html>
  `;

  res.send(html);
});

app.listen(port, () => console.log(`Listening on ${port}`));