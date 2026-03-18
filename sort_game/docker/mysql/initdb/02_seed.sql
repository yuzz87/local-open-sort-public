INSERT INTO algorithms (name, complexity, is_active) VALUES
  ('bubble', 'O(n^2)', TRUE),
  ('selection', 'O(n^2)', TRUE),
  ('insertion', 'O(n^2)', TRUE),
  ('merge', 'O(n log n)', TRUE),
  ('quick', 'O(n log n)', TRUE),
  ('heap', 'O(n log n)', TRUE)
ON DUPLICATE KEY UPDATE
  complexity = VALUES(complexity),
  is_active = VALUES(is_active);

INSERT INTO users (username, email, password_hash) VALUES
  (
    'testuser1234',
    'test@1234.com',
    '$2b$12$IauWlwfdQST.9g0m79SzbeVezfrwUR4yl3LHigczlMuaJJFHF/Z0q'
  )
ON DUPLICATE KEY UPDATE
  username = VALUES(username),
  password_hash = VALUES(password_hash);