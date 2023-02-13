1. That the auth_user_id does not need to be assigned in any particular way (by encoding or time of registration etc.)
2. That for channel_messages and dm_messages that the start message i.e message\[0\] is the most recent message and the last message\[len(messages)\] is the earliest. 
3. That any user in a DM is treated as an "owner" and can edit anyone else's messages
4. That if a user sets their email or handle to what it is currently there is no error
