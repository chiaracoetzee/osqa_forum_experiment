DELETE FROM forum_subscriptionsettings WHERE user_id IN (SELECT id FROM auth_user WHERE email='derrickccoetzee@gmail.com');
DELETE FROM forum_validationhash WHERE user_id IN (SELECT id FROM auth_user WHERE email='derrickccoetzee@gmail.com');
DELETE FROM forum_authkeyuserassociation WHERE user_id IN (SELECT id FROM auth_user WHERE email='derrickccoetzee@gmail.com');
DELETE FROM forum_actionrepute WHERE action_id IN (SELECT id FROM forum_action WHERE user_id IN (SELECT id FROM auth_user WHERE email='derrickccoetzee@gmail.com'));
DELETE FROM forum_action WHERE user_id IN (SELECT id FROM auth_user WHERE email='derrickccoetzee@gmail.com');
DELETE FROM forum_user WHERE user_ptr_id IN (SELECT id FROM auth_user WHERE email='derrickccoetzee@gmail.com');
DELETE FROM auth_message WHERE user_id IN (SELECT id FROM auth_user WHERE email='derrickccoetzee@gmail.com');
DELETE FROM auth_user WHERE email='derrickccoetzee@gmail.com';
