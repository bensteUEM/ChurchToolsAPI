#!/bin/bash

#Sample from CT
#curl -X POST http://churchtools.test/api/files/avatar/1 -H 'cookie: ChurchTools_template=nmtncfh5kushiqp9ikidn27n66' -H 'content-type: multipart/form-data' -F 'files[]=@/Users/david/Downloads/8BS_6600.JPG;type=image/jpeg' -H 'csrf-token: db639402f593da794d99aa2706339314da62a7c0dbcc3bb8c505d82d6702b73e'

<<'Block_comment'
curl -X POST http://churchtools.test/api/files/avatar/1 \
  -H 'cookie: ChurchTools_template=nmtncfh5kushiqp9ikidn27n66' \
  -H 'content-type: multipart/form-data' \
  -F 'files[]=@/Users/david/Downloads/8BS_6600.JPG;type=image/jpeg' \
  -H 'csrf-token: db639402f593da794d99aa2706339314da62a7c0dbcc3bb8c505d82d6702b73e'
*/
Block_comment

#curl -X GET https://elkw1610.krz.tools/api/whoami \ -H 'Authorization': 'Login wTjKUXCCHewQJS7SIAK7sG7ucCVIcheUKSsaNsVhFyu7LbmrmzVUgm4yMOm4F1As1Vy2cNIha8oL1V7uuTb24w3Bd1r56KlQSJXhg4jl354w5kEoXQvMMRgJceQ82cq7Ssuj5EuNqp2sQLKv5abRgWYx0VsP4lEQJh3ct1ItBqU4hLCCB2wQG3Dk2UJBlhSLJEAwndE98HO5Ygidj5AfRzA0RCuQHg4xMUHMi0IeAMkSKTPy7WplnwOe7CIVgtjK' -c script_cookie

<<'Block_comment'
 - This works !
#Tried getting Cookie from FF Storage and CSRF from REST API GUI - avatar pic test user
curl -X POST https://elkw1610.krz.tools/api/files/avatar/229 \
  -H 'cookie: ChurchTools_ct_elkw1610=ns43rfdhljlifn932b6ab862c7' \
  -H 'content-type: multipart/form-data' \
  -H 'csrf-token: 3a3b150516ba0e4a759203e7cc1f9550f6023f6e1272cf5c6dfdad80e036955b' \
  -F 'files[]=@media/pinguin.png;type=image/png'

Block_comment

<<'Block_comment'
 - This works !
#using Cookie from FF Storage and CSRF from REST API GUI - song
curl -X DELETE https://elkw1610.krz.tools/api/files/song_arrangement/394 \
  -H 'cookie: ChurchTools_ct_elkw1610=ns43rfdhljlifn932b6ab862c7' \
  -H 'content-type: multipart/form-data' \
  -H 'csrf-token: 3a3b150516ba0e4a759203e7cc1f9550f6023f6e1272cf5c6dfdad80e036955b' \
Block_comment


<<'Block_comment'
 - This works ! using Cookie from FF Storage - song
curl -X POST https://elkw1610.krz.tools/api/files/song_arrangement/394 \
  -H 'cookie: ChurchTools_ct_elkw1610=ns43rfdhljlifn932b6ab862c7' \
  -H 'content-type: multipart/form-data' \
  -F 'files[]=@media/pinguin.png;type=image/png'
Block_comment


# - This works ! using Auth POST - song
curl -X POST https://elkw1610.krz.tools/api/files/song_arrangement/394 \
  -H 'Authorization: Login wTjKUXCCHewQJS7SIAK7sG7ucCVIcheUKSsaNsVhFyu7LbmrmzVUgm4yMOm4F1As1Vy2cNIha8oL1V7uuTb24w3Bd1r56KlQSJXhg4jl354w5kEoXQvMMRgJceQ82cq7Ssuj5EuNqp2sQLKv5abRgWYx0VsP4lEQJh3ct1ItBqU4hLCCB2wQG3Dk2UJBlhSLJEAwndE98HO5Ygidj5AfRzA0RCuQHg4xMUHMi0IeAMkSKTPy7WplnwOe7CIVgtjK' \
  -F 'files[]=@media/pinguin_shell.png;type=image/png'

#F Param is not file but "FORM"

<<'Block_comment'
# - This works !
#using Auth GET - song
curl -X GET https://elkw1610.krz.tools/api/files/song_arrangement/394 \
  -H 'Authorization: Login wTjKUXCCHewQJS7SIAK7sG7ucCVIcheUKSsaNsVhFyu7LbmrmzVUgm4yMOm4F1As1Vy2cNIha8oL1V7uuTb24w3Bd1r56KlQSJXhg4jl354w5kEoXQvMMRgJceQ82cq7Ssuj5EuNqp2sQLKv5abRgWYx0VsP4lEQJh3ct1ItBqU4hLCCB2wQG3Dk2UJBlhSLJEAwndE98HO5Ygidj5AfRzA0RCuQHg4xMUHMi0IeAMkSKTPy7WplnwOe7CIVgtjK' \
Block_comment