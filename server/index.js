const mappings = 'checkin_user_mappings';
const users = 'hafh72_users';
const fs = require('fs');

let mysql = require('mysql');

let config = JSON.parse(fs.readFileSync("config.json"));

let db_conn = mysql.createConnection({
    host: config.host,
    user: config.user,
    password: config.password,
    database: config.database 
});

db_conn.connect();

db_conn.query(`select * from ${users}`, (err, results, fields) => {
    if (err) {
        throw err;
    }

    for (let result of results) {
        console.log(result.user_email);
    }
});

//==========================

let express = require('express');
let app = express();

app.get('/', (req, res) => {
    res.send('Hello World');
});

app.listen(8080);

//==========================

const { spawn } = require('child_process');
const scanner = spawn('../just-use-c/dms-nfc-reader', []);

scanner.stdout.on('data', (data) => {
    console.log(`stdout: ${data.toString()}`);

    let tag_id = data.toString().split('READ:')[1];

    if (tag_id === undefined) {
        console.log('Invalid input - no code retrieved');
        return;
    }

    tag_id = tag_id.trim();
    console.log(tag_id);

    // Get the mapping for this tag.
    const qs = `select * from ${mappings} where tag_id="${tag_id}"`;
    db_conn.query(qs, (err, results, fields) => {

        if (err) {
            console.log(err);
        }
        else if (results.length > 0) {

            let user_id = results[0].user_id;

            // Get the current user assigned to this tag.
            const qs = `select user_email from ${users} where id=${user_id}`;
            db_conn.query(qs, (err, results, fields) => {

                if (results !== undefined && results.length > 0) {
                    let email = results[0];

                    // Get this user's current check-in state.
                    const qs = `select state from checkin_state where user_id=${user_id}`;
                    db_conn.query(qs, (err, results, fields) => {

                        if (err) {
                            console.log(err);
                        }
                        else if (results.length > 0) {

                            const state = results[0].state;
                            const new_state = 1 - state;

                            let sound_to_play = '';
                            if (new_state == 1) {
                                //sound_to_play = 'check_in.wav';
                                sound_to_play = 'checkin_ross.wav';
                            } else {
                                sound_to_play = 'check_out.wav';
                            }
                            
                            // Update this user's check-in state.

                            const qs = `update checkin_state set state=${new_state} where user_id=${user_id}`;

                            console.log(qs);

                            db_conn.query(qs, (err, results, fields) => {

                                if (err) {
                                    console.log(err);
                                } else {
                                    const sound = spawn('play', ['../' + sound_to_play]);
                                    sound.stdout.on('data', () => {});
                                }
                            });
                        }
                        else {
                            console.log('No checkin state found');
                        }
                    });
                }
            });
        }
        else {
            console.log('No results');
        }
    });
});

scanner.stderr.on('data', (data) => {
    console.log(`stderr: ${data}`);
});

scanner.on('close', (code) => {
    console.log(`child process exited with code ${code}`);
});
