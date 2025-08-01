const express = require('express');
const axios = require('axios');
const cors = require('cors');

const app = express();
const PORT = 4000;

app.use(cors());

const CLIENT_ID = 'c88190dd3b7402cb20a6bf9660a043f1'; // Replace this with your actual MAL client ID

app.get('/api/anime', async (req, res) => {
  const { q } = req.query;

  try {
    const fields = "id,title,main_picture,start_date,mean,rank,synopsis,genres";
    axios.get("https://api.myanimelist.net/v2/anime", {
      headers: { "X-MAL-CLIENT-ID": process.env.CLIENT_ID },
      params: { q: req.query.q, limit: 10, fields },
    });

    res.json(response.data);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch from MAL API' });
  }
});

app.listen(PORT, () => {
  console.log(`✅ Backend running at http://localhost:${PORT}`);
});
