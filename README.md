# kdbTwitter
KDB Twitter Feed

There are 3 steps needed to start the feed.

Step 1 - Edit the AUTH_DICTIONARY dictionary in feed.py to include your own user's credientials.

Step 2 - Start a q instance on port 3000 and run the update.q script.  A different port can be selected, but a corresponding update in feed.q must also be made.
    > q update.q -p 3000
    > q)

Step 3 - Start data retrieval and forwarding by running feed.py
    > ./feed.py

At this point, the feed should be running, and tweets should be collecting in KDB.  To verify that the count of tweets is increasing, run these commands at the q prompt:
    > q) .z.ts:{show count tweets};
    > q) \t 1000

The count of rows in the 'tweets' table should be displayed at the console, and be increasing.

To view the contents of the table:
    > q) 5#tweets
    
