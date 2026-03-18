-- ==========================================
-- users
-- login 用に email / password_hash を追加
-- ==========================================

CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,

  username VARCHAR(50) NOT NULL,
  email VARCHAR(255) NOT NULL,
  password_hash VARCHAR(255) NOT NULL,

  is_active BOOLEAN NOT NULL DEFAULT TRUE,

  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    ON UPDATE CURRENT_TIMESTAMP,
  deleted_at DATETIME DEFAULT NULL,

  UNIQUE KEY uq_username (username),
  UNIQUE KEY uq_users_email (email),

  INDEX idx_users_active (is_active),
  INDEX idx_users_deleted_at (deleted_at)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;


-- ==========================================
-- algorithms (master table)
-- ==========================================

CREATE TABLE IF NOT EXISTS algorithms (
  id INT AUTO_INCREMENT PRIMARY KEY,

  name VARCHAR(30) NOT NULL,
  complexity VARCHAR(50) DEFAULT NULL COMMENT 'Time complexity',

  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

  UNIQUE KEY uq_algorithm_name (name),
  INDEX idx_algorithms_active (is_active)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;


-- ==========================================
-- battles
-- Guest は保存しないため user_id は NOT NULL
-- 1回の実行セットを表す
-- ==========================================

CREATE TABLE IF NOT EXISTS battles (
  id INT AUTO_INCREMENT PRIMARY KEY,

  user_id INT NOT NULL,

  array_size INT NOT NULL,
  benchmark_size INT NOT NULL,

  status VARCHAR(20) NOT NULL DEFAULT 'COMPLETED',

  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    ON UPDATE CURRENT_TIMESTAMP,

  INDEX idx_battles_user_id (user_id),
  INDEX idx_battles_created_at (created_at),
  INDEX idx_battles_status (status),
  INDEX idx_battles_user_created_at (user_id, created_at),

  CONSTRAINT fk_battles_user
    FOREIGN KEY (user_id)
    REFERENCES users(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  CONSTRAINT chk_battles_array_size
    CHECK (array_size BETWEEN 5 AND 100),

  CONSTRAINT chk_battles_benchmark_size
    CHECK (benchmark_size BETWEEN 100 AND 10000),

  CONSTRAINT chk_battles_status
    CHECK (status IN ('COMPLETED'))
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;


-- ==========================================
-- battle_results
-- battles に属する各アルゴリズム結果
-- ==========================================

CREATE TABLE IF NOT EXISTS battle_results (
  id INT AUTO_INCREMENT PRIMARY KEY,

  battle_id INT NOT NULL,
  algorithm_id INT NOT NULL,

  duration_ms DECIMAL(12, 3) NOT NULL,
  rank_position INT NOT NULL,

  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

  UNIQUE KEY uq_battle_results_rank (battle_id, rank_position),
  UNIQUE KEY uq_battle_results_algorithm (battle_id, algorithm_id),

  INDEX idx_battle_results_battle_id (battle_id),
  INDEX idx_battle_results_algorithm_id (algorithm_id),
  INDEX idx_battle_results_rank_position (rank_position),
  INDEX idx_battle_results_duration_ms (duration_ms),

  CONSTRAINT fk_battle_results_battle
    FOREIGN KEY (battle_id)
    REFERENCES battles(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,

  CONSTRAINT fk_battle_results_algorithm
    FOREIGN KEY (algorithm_id)
    REFERENCES algorithms(id)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,

  CONSTRAINT chk_battle_results_duration_ms
    CHECK (duration_ms >= 0),

  CONSTRAINT chk_battle_results_rank_position
    CHECK (rank_position BETWEEN 1 AND 6)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;


-- ==========================================
-- login_attempts (optional)
-- ログイン失敗監視・レート制限補助用
-- ==========================================

CREATE TABLE IF NOT EXISTS login_attempts (
  id INT AUTO_INCREMENT PRIMARY KEY,

  email VARCHAR(255) NOT NULL,
  ip_address VARCHAR(45) NOT NULL,
  is_success BOOLEAN NOT NULL DEFAULT FALSE,

  attempted_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

  INDEX idx_login_attempts_email (email),
  INDEX idx_login_attempts_ip_address (ip_address),
  INDEX idx_login_attempts_attempted_at (attempted_at)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;