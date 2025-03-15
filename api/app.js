const { exec } = require('child_process');
const fs = require('fs')
const express = require('express')
var https = require('https')
var http = require('http')

//import keys, assuming you installed them with certbot
var privateKey = fs.readFileSync('/etc/letsencrypt/live/api.sagent.bio/fullchain.pem');
var certificate = fs.readFileSync('/etc/letsencrypt/live/api.sagent.bio/privkey.pem');

const app = express()
//const port = 3000

http.createServer(app).listen(80)
https.createServer({
    key: privateKey,
    cert: certificate
}, app).listen(443)
console.log('RM FOLD HTTPS server starting on port 443 ')
console.log('RM FOLD HTTP server starting on port 80')


// Disable CORS: Allow all origins
app.use((req, res, next) => {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', '*');
    next();
});

app.get("/", async (req, res) => {
    res.send("Hello! Head to /run to run sfold")
})

//file helper functions
function writeSequenceToFile(sequence, name) {
    const content = `>${name}\n${sequence}\n`;
    console.log(content)
    fs.writeFileSync('./sequence.txt', content, 'utf8');
}
function deleteFile(filename) {
    try {
        fs.unlinkSync(filename);
        console.log(`${filename} deleted successfully.`);
    } catch (err) {
        console.error(`Error deleting ${filename}:`, err.message);
    }
}


app.get('/run:query?', (req, res) => {
    console.log(req.query);
    const data = req.query;
    const sequence = data.sequence
    const name = data.name

    console.log(sequence)
    console.log(name)
    if (!sequence) {
        throw new Error('Must have query parameter sequence')
    }

    if (!name) {
        throw new Error('Must have query parameter name')
    }

    //write the sequence to file
    writeSequenceToFile(sequence, name)

    //option -i 2 runs soligo
    exec('/home/admin/repos/sagent/bin/sfold -i 2  ./sequence.txt', (error, stdout, stderr) => {
        if (error) {
            console.error(`exec error: ${error}`);
            return;
        }
        console.log(`stdout: ${stdout}`);
        console.error(`stderr: ${stderr}`);
        deleteFile('sequence.txt');

        exec("zip -r outputs.zip output", (zipError, zipStdout, zipStderr) => {
            if (zipError) {
                console.error(`zip error: ${zipError}`);
                return res.status(500).send('Error zipping outputs');
            }

            console.log(`zip stdout: ${zipStdout}`);
            console.error(`zip stderr: ${zipStderr}`);

            // Send the zip file to the client
            res.download('./outputs.zip', 'outputs.zip', (err) => {
                if (err) {
                    console.error(`Error sending file: ${err}`);
                } else {
                    console.log('outputs.zip sent successfully.');
                    fs.unlinkSync('./outputs.zip'); // Delete zip after sending
                }
            });

        })
    });

    //res.send({ data: "Data" });
});

app.get('/fetch_output/oligo', (req, res) => {
    const data = req
    fs.readFile('/home/admin/repos/sagent/api/output/oligo.out', 'utf8', (err, data) => {
        const re = /\d+-.+/g;
        const rows = data.match(re);

        let responseData = [];
        for (let i = 0; i < rows.length; i++) {
            let tmpBe = rows[i].match(/[\d|\.|-]+\d  \d$/)[0];

            let rowData = {
                start: rows[i].match(/^\d+/)[0],
                end: rows[i].match(/(?: )(\d+)/)[0],
                aso: rows[i].match(/[A-Z]+(?:  )/)[0],
                gc: rows[i].match(/\d+\.\d%/)[0],
                be: tmpBe.match(/[\d|\.|-]+\d/)[0],
                gggg: rows[i].match(/\d+$/)[0]
            };
            responseData.push(rowData);
        }
        res.json({ oligo: responseData });
    });
})

/* app.listen(port, () => {
    console.log(`RM Fold listening on port ${port}`)
}); */