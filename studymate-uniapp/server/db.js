consconst Database = require('better-sqlite3');
const path = require('path');

consconst Database = require('better-sqlite3');
const path = require('path');

const dbPath = path.join(__dirname, 'studymate.db');
const db = new Databasconst Database = require('better-sqlite3');
const path = require('path');

const dbPath = path.join(__dirname, 'studymate.db');
const db = new Database(dbPath);

// 启用 WAL 模式提升并发性能
db.pragma('journalconst Database = require('better-sqlite3');
const path = require('path');

const dbPath = path.join(__dirname, 'studymate.db');
const db = new Database(dbPath);

// 启用 WAL 模式提升并发性能
db.pragma('journal_mode = WAL');
db.pragma('foreign_keys = ON');

function initDBconst Database = require('better-sqlite3');
const path = require('path');

const dbPath = path.join(__dirname, 'studymate.db');
const db = new Database(dbPath);

// 启用 WAL 模式提升并发性能
db.pragma('journal_mode = WAL');
db.pragma('foreign_keys = ON');

function initDB() {
  db.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id TEXT PRIMARYconst Database = require('better-sqlite3');
const path = require('path');

const dbPath = path.join(__dirname, 'studymate.db');
const db = new Database(dbPath);

// 启用 WAL 模式提升并发性能
db.pragma('journal_mode = WAL');
db.pragma('foreign_keys = ON');

function initDB() {
  db.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id TEXT PRIMARY KEY,
      email TEXT UNIQUE NOT NULL,
      password_hash TEXT NOT NULL,
      nickname TEXTconst Database = require('better-sqlite3');
const path = require('path');

const dbPath = path.join(__dirname, 'studymate.db');
const db = new Database(dbPath);

// 启用 WAL 模式提升并发性能
db.pragma('journal_mode = WAL');
db.pragma('foreign_keys = ON');

function initDB() {
  db.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id TEXT PRIMARY KEY,
      email TEXT UNIQUE NOT NULL,
      password_hash TEXT NOT NULL,
      nickname TEXT,
      avatar_url TEXT,
      created_at TEXT DEFAULT (datetime('now'))
    );const Database = require('better-sqlite3');
const path = require('path');

const dbPath = path.join(__dirname, 'studymate.db');
const db = new Database(dbPath);

// 启用 WAL 模式提升并发性能
db.pragma('journal_mode = WAL');
db.pragma('foreign_keys = ON');

function initDB() {
  db.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id TEXT PRIMARY KEY,
      email TEXT UNIQUE NOT NULL,
      password_hash TEXT NOT NULL,
      nickname TEXT,
      avatar_url TEXT,
      created_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS study_plans (
      id TEXT PRIMARY KEY,
      user_id TEXT NOT NULL,
      exam_name TEXT NOT NULL,
      exam_date TEXT,
      target_sconst Database = require('better-sqlite3');
const path = require('path');

const dbPath = path.join(__dirname, 'studymate.db');
const db = new Database(dbPath);

// 启用 WAL 模式提升并发性能
db.pragma('journal_mode = WAL');
db.pragma('foreign_keys = ON');

function initDB() {
  db.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id TEXT PRIMARY KEY,
      email TEXT UNIQUE NOT NULL,
      password_hash TEXT NOT NULL,
      nickname TEXT,
      avatar_url TEXT,
      created_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS study_plans (
      id TEXT PRIMARY KEY,
      user_id TEXT NOT NULL,
      exam_name TEXT NOT NULL,
      exam_date TEXT,
      target_scores TEXT DEFAULT '{}',
      daily_study_time INTEGER DEFAULT 0,
      weakconst Database = require('better-sqlite3');
const path = require('path');

const dbPath = path.join(__dirname, 'studymate.db');
const db = new Database(dbPath);

// 启用 WAL 模式提升并发性能
db.pragma('journal_mode = WAL');
db.pragma('foreign_keys = ON');

function initDB() {
  db.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id TEXT PRIMARY KEY,
      email TEXT UNIQUE NOT NULL,
      password_hash TEXT NOT NULL,
      nickname TEXT,
      avatar_url TEXT,
      created_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS study_plans (
      id TEXT PRIMARY KEY,
      user_id TEXT NOT NULL,
      exam_name TEXT NOT NULL,
      exam_date TEXT,
      target_scores TEXT DEFAULT '{}',
      daily_study_time INTEGER DEFAULT 0,
      weak_points TEXT DEFAULT '[]',
      study_phase TEXT DEFAULT 'planning',
      notes TEXTconst Database = require('better-sqlite3');
const path = require('path');

const dbPath = path.join(__dirname, 'studymate.db');
const db = new Database(dbPath);

// 启用 WAL 模式提升并发性能
db.pragma('journal_mode = WAL');
db.pragma('foreign_keys = ON');

function initDB() {
  db.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id TEXT PRIMARY KEY,
      email TEXT UNIQUE NOT NULL,
      password_hash TEXT NOT NULL,
      nickname TEXT,
      avatar_url TEXT,
      created_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS study_plans (
      id TEXT PRIMARY KEY,
      user_id TEXT NOT NULL,
      exam_name TEXT NOT NULL,
      exam_date TEXT,
      target_scores TEXT DEFAULT '{}',
      daily_study_time INTEGER DEFAULT 0,
      weak_points TEXT DEFAULT '[]',
      study_phase TEXT DEFAULT 'planning',
      notes TEXT DEFAULT '',
      ai_plan TEXT,
      created_at TEXT DEFAULT (datetime('now')),
      FOREIGNconst Database = require('better-sqlite3');
const path = require('path');

const dbPath = path.join(__dirname, 'studymate.db');
const db = new Database(dbPath);

// 启用 WAL 模式提升并发性能
db.pragma('journal_mode = WAL');
db.pragma('foreign_keys = ON');

function initDB() {
  db.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id TEXT PRIMARY KEY,
      email TEXT UNIQUE NOT NULL,
      password_hash TEXT NOT NULL,
      nickname TEXT,
      avatar_url TEXT,
      created_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS study_plans (
      id TEXT PRIMARY KEY,
      user_id TEXT NOT NULL,
      exam_name TEXT NOT NULL,
      exam_date TEXT,
      target_scores TEXT DEFAULT '{}',
      daily_study_time INTEGER DEFAULT 0,
      weak_points TEXT DEFAULT '[]',
      study_phase TEXT DEFAULT 'planning',
      notes TEXT DEFAULT '',
      ai_plan TEXT,
      created_at TEXT DEFAULT (datetime('now')),
      FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS daily_const Database = require('better-sqlite3');
const path = require('path');

const dbPath = path.join(__dirname, 'studymate.db');
const db = new Database(dbPath);

// 启用 WAL 模式提升并发性能
db.pragma('journal_mode = WAL');
db.pragma('foreign_keys = ON');

function initDB() {
  db.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id TEXT PRIMARY KEY,
      email TEXT UNIQUE NOT NULL,
      password_hash TEXT NOT NULL,
      nickname TEXT,
      avatar_url TEXT,
      created_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS study_plans (
      id TEXT PRIMARY KEY,
      user_id TEXT NOT NULL,
      exam_name TEXT NOT NULL,
      exam_date TEXT,
      target_scores TEXT DEFAULT '{}',
      daily_study_time INTEGER DEFAULT 0,
      weak_points TEXT DEFAULT '[]',
      study_phase TEXT DEFAULT 'planning',
      notes TEXT DEFAULT '',
      ai_plan TEXT,
      created_at TEXT DEFAULT (datetime('now')),
      FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS daily_tasks (
      id TEXT PRIMARY KEY,
      plan_id TEXT NOT NULL,
      date TEXT NOTconst Database = require('better-sqlite3');
const path = require('path');

const dbPath = path.join(__dirname, 'studymate.db');
const db = new Database(dbPath);

// 启用 WAL 模式提升并发性能
db.pragma('journal_mode = WAL');
db.pragma('foreign_keys = ON');

function initDB() {
  db.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id TEXT PRIMARY KEY,
      email TEXT UNIQUE NOT NULL,
      password_hash TEXT NOT NULL,
      nickname TEXT,
      avatar_url TEXT,
      created_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS study_plans (
      id TEXT PRIMARY KEY,
      user_id TEXT NOT NULL,
      exam_name TEXT NOT NULL,
      exam_date TEXT,
      target_scores TEXT DEFAULT '{}',
      daily_study_time INTEGER DEFAULT 0,
      weak_points TEXT DEFAULT '[]',
      study_phase TEXT DEFAULT 'planning',
      notes TEXT DEFAULT '',
      ai_plan TEXT,
      created_at TEXT DEFAULT (datetime('now')),
      FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS daily_tasks (
      id TEXT PRIMARY KEY,
      plan_id TEXT NOT NULL,
      date TEXT NOT NULL,
      type TEXT NOT NULL,
      subject TEXT NOT NULL,
      content TEXT NOT NULL,const Database = require('better-sqlite3');
const path = require('path');

const dbPath = path.join(__dirname, 'studymate.db');
const db = new Database(dbPath);

// 启用 WAL 模式提升并发性能
db.pragma('journal_mode = WAL');
db.pragma('foreign_keys = ON');

function initDB() {
  db.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id TEXT PRIMARY KEY,
      email TEXT UNIQUE NOT NULL,
      password_hash TEXT NOT NULL,
      nickname TEXT,
      avatar_url TEXT,
      created_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS study_plans (
      id TEXT PRIMARY KEY,
      user_id TEXT NOT NULL,
      exam_name TEXT NOT NULL,
      exam_date TEXT,
      target_scores TEXT DEFAULT '{}',
      daily_study_time INTEGER DEFAULT 0,
      weak_points TEXT DEFAULT '[]',
      study_phase TEXT DEFAULT 'planning',
      notes TEXT DEFAULT '',
      ai_plan TEXT,
      created_at TEXT DEFAULT (datetime('now')),
      FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS daily_tasks (
      id TEXT PRIMARY KEY,
      plan_id TEXT NOT NULL,
      date TEXT NOT NULL,
      type TEXT NOT NULL,
      subject TEXT NOT NULL,
      content TEXT NOT NULL,
      duration INTEGER DEFAULT 0,
      status TEXT DEFAULT 'pending',
      completed_at TEXTconst Database = require('better-sqlite3');
const path = require('path');

const dbPath = path.join(__dirname, 'studymate.db');
const db = new Database(dbPath);

// 启用 WAL 模式提升并发性能
db.pragma('journal_mode = WAL');
db.pragma('foreign_keys = ON');

function initDB() {
  db.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id TEXT PRIMARY KEY,
      email TEXT UNIQUE NOT NULL,
      password_hash TEXT NOT NULL,
      nickname TEXT,
      avatar_url TEXT,
      created_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS study_plans (
      id TEXT PRIMARY KEY,
      user_id TEXT NOT NULL,
      exam_name TEXT NOT NULL,
      exam_date TEXT,
      target_scores TEXT DEFAULT '{}',
      daily_study_time INTEGER DEFAULT 0,
      weak_points TEXT DEFAULT '[]',
      study_phase TEXT DEFAULT 'planning',
      notes TEXT DEFAULT '',
      ai_plan TEXT,
      created_at TEXT DEFAULT (datetime('now')),
      FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS daily_tasks (
      id TEXT PRIMARY KEY,
      plan_id TEXT NOT NULL,
      date TEXT NOT NULL,
      type TEXT NOT NULL,
      subject TEXT NOT NULL,
      content TEXT NOT NULL,
      duration INTEGER DEFAULT 0,
      status TEXT DEFAULT 'pending',
      completed_at TEXT,
      proof_image_url TEXT,
      created_at TEXT DEFAULT (datetime('now')),
      FOREIGNconst Database = require('better-sqlite3');
const path = require('path');

const dbPath = path.join(__dirname, 'studymate.db');
const db = new Database(dbPath);

// 启用 WAL 模式提升并发性能
db.pragma('journal_mode = WAL');
db.pragma('foreign_keys = ON');

function initDB() {
  db.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id TEXT PRIMARY KEY,
      email TEXT UNIQUE NOT NULL,
      password_hash TEXT NOT NULL,
      nickname TEXT,
      avatar_url TEXT,
      created_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS study_plans (
      id TEXT PRIMARY KEY,
      user_id TEXT NOT NULL,
      exam_name TEXT NOT NULL,
      exam_date TEXT,
      target_scores TEXT DEFAULT '{}',
      daily_study_time INTEGER DEFAULT 0,
      weak_points TEXT DEFAULT '[]',
      study_phase TEXT DEFAULT 'planning',
      notes TEXT DEFAULT '',
      ai_plan TEXT,
      created_at TEXT DEFAULT (datetime('now')),
      FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS daily_tasks (
      id TEXT PRIMARY KEY,
      plan_id TEXT NOT NULL,
      date TEXT NOT NULL,
      type TEXT NOT NULL,
      subject TEXT NOT NULL,
      content TEXT NOT NULL,
      duration INTEGER DEFAULT 0,
      status TEXT DEFAULT 'pending',
      completed_at TEXT,
      proof_image_url TEXT,
      created_at TEXT DEFAULT (datetime('now')),
      FOREIGN KEY (plan_id) REFERENCES study_plans(id)
    );

    CREATE TABLE IF NOT EXISTconst Database = require('better-sqlite3');
const path = require('path');

const dbPath = path.join(__dirname, 'studymate.db');
const db = new Database(dbPath);

// 启用 WAL 模式提升并发性能
db.pragma('journal_mode = WAL');
db.pragma('foreign_keys = ON');

function initDB() {
  db.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id TEXT PRIMARY KEY,
      email TEXT UNIQUE NOT NULL,
      password_hash TEXT NOT NULL,
      nickname TEXT,
      avatar_url TEXT,
      created_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS study_plans (
      id TEXT PRIMARY KEY,
      user_id TEXT NOT NULL,
      exam_name TEXT NOT NULL,
      exam_date TEXT,
      target_scores TEXT DEFAULT '{}',
      daily_study_time INTEGER DEFAULT 0,
      weak_points TEXT DEFAULT '[]',
      study_phase TEXT DEFAULT 'planning',
      notes TEXT DEFAULT '',
      ai_plan TEXT,
      created_at TEXT DEFAULT (datetime('now')),
      FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS daily_tasks (
      id TEXT PRIMARY KEY,
      plan_id TEXT NOT NULL,
      date TEXT NOT NULL,
      type TEXT NOT NULL,
      subject TEXT NOT NULL,
      content TEXT NOT NULL,
      duration INTEGER DEFAULT 0,
      status TEXT DEFAULT 'pending',
      completed_at TEXT,
      proof_image_url TEXT,
      created_at TEXT DEFAULT (datetime('now')),
      FOREIGN KEY (plan_id) REFERENCES study_plans(id)
    );

    CREATE TABLE IF NOT EXISTS flash_cards (
      id TEXT PRIMARY KEY,
      plan_id TEXT NOT NULL,const Database = require('better-sqlite3');
const path = require('path');

const dbPath = path.join(__dirname, 'studymate.db');
const db = new Database(dbPath);

// 启用 WAL 模式提升并发性能
db.pragma('journal_mode = WAL');
db.pragma('foreign_keys = ON');

function initDB() {
  db.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id TEXT PRIMARY KEY,
      email TEXT UNIQUE NOT NULL,
      password_hash TEXT NOT NULL,
      nickname TEXT,
      avatar_url TEXT,
      created_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS study_plans (
      id TEXT PRIMARY KEY,
      user_id TEXT NOT NULL,
      exam_name TEXT NOT NULL,
      exam_date TEXT,
      target_scores TEXT DEFAULT '{}',
      daily_study_time INTEGER DEFAULT 0,
      weak_points TEXT DEFAULT '[]',
      study_phase TEXT DEFAULT 'planning',
      notes TEXT DEFAULT '',
      ai_plan TEXT,
      created_at TEXT DEFAULT (datetime('now')),
      FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS daily_tasks (
      id TEXT PRIMARY KEY,
      plan_id TEXT NOT NULL,
      date TEXT NOT NULL,
      type TEXT NOT NULL,
      subject TEXT NOT NULL,
      content TEXT NOT NULL,
      duration INTEGER DEFAULT 0,
      status TEXT DEFAULT 'pending',
      completed_at TEXT,
      proof_image_url TEXT,
      created_at TEXT DEFAULT (datetime('now')),
      FOREIGN KEY (plan_id) REFERENCES study_plans(id)
    );

    CREATE TABLE IF NOT EXISTS flash_cards (
      id TEXT PRIMARY KEY,
      plan_id TEXT NOT NULL,
      question TEXT NOT NULL,
      answer TEXT NOT NULL,
      subject TEXT NOT NULL,
      masteryconst Database = require('better-sqlite3');
const path = require('path');

const dbPath = path.join(__dirname, 'studymate.db');
const db = new Database(dbPath);

// 启用 WAL 模式提升并发性能
db.pragma('journal_mode = WAL');
db.pragma('foreign_keys = ON');

function initDB() {
  db.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id TEXT PRIMARY KEY,
      email TEXT UNIQUE NOT NULL,
      password_hash TEXT NOT NULL,
      nickname TEXT,
      avatar_url TEXT,
      created_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS study_plans (
      id TEXT PRIMARY KEY,
      user_id TEXT NOT NULL,
      exam_name TEXT NOT NULL,
      exam_date TEXT,
      target_scores TEXT DEFAULT '{}',
      daily_study_time INTEGER DEFAULT 0,
      weak_points TEXT DEFAULT '[]',
      study_phase TEXT DEFAULT 'planning',
      notes TEXT DEFAULT '',
      ai_plan TEXT,
      created_at TEXT DEFAULT (datetime('now')),
      FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS daily_tasks (
      id TEXT PRIMARY KEY,
      plan_id TEXT NOT NULL,
      date TEXT NOT NULL,
      type TEXT NOT NULL,
      subject TEXT NOT NULL,
      content TEXT NOT NULL,
      duration INTEGER DEFAULT 0,
      status TEXT DEFAULT 'pending',
      completed_at TEXT,
      proof_image_url TEXT,
      created_at TEXT DEFAULT (datetime('now')),
      FOREIGN KEY (plan_id) REFERENCES study_plans(id)
    );

    CREATE TABLE IF NOT EXISTS flash_cards (
      id TEXT PRIMARY KEY,
      plan_id TEXT NOT NULL,
      question TEXT NOT NULL,
      answer TEXT NOT NULL,
      subject TEXT NOT NULL,
      mastery_level INTEGER DEFAULT 0,
      next_review_date TEXT,
      review_count INTEGER DEFAULTconst Database = require('better-sqlite3');
const path = require('path');

const dbPath = path.join(__dirname, 'studymate.db');
const db = new Database(dbPath);

// 启用 WAL 模式提升并发性能
db.pragma('journal_mode = WAL');
db.pragma('foreign_keys = ON');

function initDB() {
  db.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id TEXT PRIMARY KEY,
      email TEXT UNIQUE NOT NULL,
      password_hash TEXT NOT NULL,
      nickname TEXT,
      avatar_url TEXT,
      created_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS study_plans (
      id TEXT PRIMARY KEY,
      user_id TEXT NOT NULL,
      exam_name TEXT NOT NULL,
      exam_date TEXT,
      target_scores TEXT DEFAULT '{}',
      daily_study_time INTEGER DEFAULT 0,
      weak_points TEXT DEFAULT '[]',
      study_phase TEXT DEFAULT 'planning',
      notes TEXT DEFAULT '',
      ai_plan TEXT,
      created_at TEXT DEFAULT (datetime('now')),
      FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS daily_tasks (
      id TEXT PRIMARY KEY,
      plan_id TEXT NOT NULL,
      date TEXT NOT NULL,
      type TEXT NOT NULL,
      subject TEXT NOT NULL,
      content TEXT NOT NULL,
      duration INTEGER DEFAULT 0,
      status TEXT DEFAULT 'pending',
      completed_at TEXT,
      proof_image_url TEXT,
      created_at TEXT DEFAULT (datetime('now')),
      FOREIGN KEY (plan_id) REFERENCES study_plans(id)
    );

    CREATE TABLE IF NOT EXISTS flash_cards (
      id TEXT PRIMARY KEY,
      plan_id TEXT NOT NULL,
      question TEXT NOT NULL,
      answer TEXT NOT NULL,
      subject TEXT NOT NULL,
      mastery_level INTEGER DEFAULT 0,
      next_review_date TEXT,
      review_count INTEGER DEFAULT 0,
      created_at TEXT DEFAULT (datetime('now')),
      updated_at TEXT DEFAULT (datetime('const Database = require('better-sqlite3');
const path = require('path');

const dbPath = path.join(__dirname, 'studymate.db');
const db = new Database(dbPath);

// 启用 WAL 模式提升并发性能
db.pragma('journal_mode = WAL');
db.pragma('foreign_keys = ON');

function initDB() {
  db.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id TEXT PRIMARY KEY,
      email TEXT UNIQUE NOT NULL,
      password_hash TEXT NOT NULL,
      nickname TEXT,
      avatar_url TEXT,
      created_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS study_plans (
      id TEXT PRIMARY KEY,
      user_id TEXT NOT NULL,
      exam_name TEXT NOT NULL,
      exam_date TEXT,
      target_scores TEXT DEFAULT '{}',
      daily_study_time INTEGER DEFAULT 0,
      weak_points TEXT DEFAULT '[]',
      study_phase TEXT DEFAULT 'planning',
      notes TEXT DEFAULT '',
      ai_plan TEXT,
      created_at TEXT DEFAULT (datetime('now')),
      FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS daily_tasks (
      id TEXT PRIMARY KEY,
      plan_id TEXT NOT NULL,
      date TEXT NOT NULL,
      type TEXT NOT NULL,
      subject TEXT NOT NULL,
      content TEXT NOT NULL,
      duration INTEGER DEFAULT 0,
      status TEXT DEFAULT 'pending',
      completed_at TEXT,
      proof_image_url TEXT,
      created_at TEXT DEFAULT (datetime('now')),
      FOREIGN KEY (plan_id) REFERENCES study_plans(id)
    );

    CREATE TABLE IF NOT EXISTS flash_cards (
      id TEXT PRIMARY KEY,
      plan_id TEXT NOT NULL,
      question TEXT NOT NULL,
      answer TEXT NOT NULL,
      subject TEXT NOT NULL,
      mastery_level INTEGER DEFAULT 0,
      next_review_date TEXT,
      review_count INTEGER DEFAULT 0,
      created_at TEXT DEFAULT (datetime('now')),
      updated_at TEXT DEFAULT (datetime('now')),
      FOREIGN KEY (plan_id) REFERENCES study_plans(id)
    );const Database = require('better-sqlite3');
const path = require('path');

const dbPath = path.join(__dirname, 'studymate.db');
const db = new Database(dbPath);

// 启用 WAL 模式提升并发性能
db.pragma('journal_mode = WAL');
db.pragma('foreign_keys = ON');

function initDB() {
  db.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id TEXT PRIMARY KEY,
      email TEXT UNIQUE NOT NULL,
      password_hash TEXT NOT NULL,
      nickname TEXT,
      avatar_url TEXT,
      created_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS study_plans (
      id TEXT PRIMARY KEY,
      user_id TEXT NOT NULL,
      exam_name TEXT NOT NULL,
      exam_date TEXT,
      target_scores TEXT DEFAULT '{}',
      daily_study_time INTEGER DEFAULT 0,
      weak_points TEXT DEFAULT '[]',
      study_phase TEXT DEFAULT 'planning',
      notes TEXT DEFAULT '',
      ai_plan TEXT,
      created_at TEXT DEFAULT (datetime('now')),
      FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS daily_tasks (
      id TEXT PRIMARY KEY,
      plan_id TEXT NOT NULL,
      date TEXT NOT NULL,
      type TEXT NOT NULL,
      subject TEXT NOT NULL,
      content TEXT NOT NULL,
      duration INTEGER DEFAULT 0,
      status TEXT DEFAULT 'pending',
      completed_at TEXT,
      proof_image_url TEXT,
      created_at TEXT DEFAULT (datetime('now')),
      FOREIGN KEY (plan_id) REFERENCES study_plans(id)
    );

    CREATE TABLE IF NOT EXISTS flash_cards (
      id TEXT PRIMARY KEY,
      plan_id TEXT NOT NULL,
      question TEXT NOT NULL,
      answer TEXT NOT NULL,
      subject TEXT NOT NULL,
      mastery_level INTEGER DEFAULT 0,
      next_review_date TEXT,
      review_count INTEGER DEFAULT 0,
      created_at TEXT DEFAULT (datetime('now')),
      updated_at TEXT DEFAULT (datetime('now')),
      FOREIGN KEY (plan_id) REFERENCES study_plans(id)
    );

    CREATE TABLE IF NOT EXISTS plants (
      id TEXT PRIMARY KEY,
      plan_id TEXT NOT NUconst Database = require('better-sqlite3');
const path = require('path');

const dbPath = path.join(__dirname, 'studymate.db');
const db = new Database(dbPath);

// 启用 WAL 模式提升并发性能
db.pragma('journal_mode = WAL');
db.pragma('foreign_keys = ON');

function initDB() {
  db.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id TEXT PRIMARY KEY,
      email TEXT UNIQUE NOT NULL,
      password_hash TEXT NOT NULL,
      nickname TEXT,
      avatar_url TEXT,
      created_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS study_plans (
      id TEXT PRIMARY KEY,
      user_id TEXT NOT NULL,
      exam_name TEXT NOT NULL,
      exam_date TEXT,
      target_scores TEXT DEFAULT '{}',
      daily_study_time INTEGER DEFAULT 0,
      weak_points TEXT DEFAULT '[]',
      study_phase TEXT DEFAULT 'planning',
      notes TEXT DEFAULT '',
      ai_plan TEXT,
      created_at TEXT DEFAULT (datetime('now')),
      FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS daily_tasks (
      id TEXT PRIMARY KEY,
      plan_id TEXT NOT NULL,
      date TEXT NOT NULL,
      type TEXT NOT NULL,
      subject TEXT NOT NULL,
      content TEXT NOT NULL,
      duration INTEGER DEFAULT 0,
      status TEXT DEFAULT 'pending',
      completed_at TEXT,
      proof_image_url TEXT,
      created_at TEXT DEFAULT (datetime('now')),
      FOREIGN KEY (plan_id) REFERENCES study_plans(id)
    );

    CREATE TABLE IF NOT EXISTS flash_cards (
      id TEXT PRIMARY KEY,
      plan_id TEXT NOT NULL,
      question TEXT NOT NULL,
      answer TEXT NOT NULL,
      subject TEXT NOT NULL,
      mastery_level INTEGER DEFAULT 0,
      next_review_date TEXT,
      review_count INTEGER DEFAULT 0,
      created_at TEXT DEFAULT (datetime('now')),
      updated_at TEXT DEFAULT (datetime('now')),
      FOREIGN KEY (plan_id) REFERENCES study_plans(id)
    );

    CREATE TABLE IF NOT EXISTS plants (
      id TEXT PRIMARY KEY,
      plan_id TEXT NOT NULL,
      type TEXT NOT NULL,
      subject TEXT NOT NULL,
      progress INTEGER DEFAULT 0const Database = require('better-sqlite3');
const path = require('path');

const dbPath = path.join(__dirname, 'studymate.db');
const db = new Database(dbPath);

// 启用 WAL 模式提升并发性能
db.pragma('journal_mode = WAL');
db.pragma('foreign_keys = ON');

function initDB() {
  db.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id TEXT PRIMARY KEY,
      email TEXT UNIQUE NOT NULL,
      password_hash TEXT NOT NULL,
      nickname TEXT,
      avatar_url TEXT,
      created_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS study_plans (
      id TEXT PRIMARY KEY,
      user_id TEXT NOT NULL,
      exam_name TEXT NOT NULL,
      exam_date TEXT,
      target_scores TEXT DEFAULT '{}',
      daily_study_time INTEGER DEFAULT 0,
      weak_points TEXT DEFAULT '[]',
      study_phase TEXT DEFAULT 'planning',
      notes TEXT DEFAULT '',
      ai_plan TEXT,
      created_at TEXT DEFAULT (datetime('now')),
      FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS daily_tasks (
      id TEXT PRIMARY KEY,
      plan_id TEXT NOT NULL,
      date TEXT NOT NULL,
      type TEXT NOT NULL,
      subject TEXT NOT NULL,
      content TEXT NOT NULL,
      duration INTEGER DEFAULT 0,
      status TEXT DEFAULT 'pending',
      completed_at TEXT,
      proof_image_url TEXT,
      created_at TEXT DEFAULT (datetime('now')),
      FOREIGN KEY (plan_id) REFERENCES study_plans(id)
    );

    CREATE TABLE IF NOT EXISTS flash_cards (
      id TEXT PRIMARY KEY,
      plan_id TEXT NOT NULL,
      question TEXT NOT NULL,
      answer TEXT NOT NULL,
      subject TEXT NOT NULL,
      mastery_level INTEGER DEFAULT 0,
      next_review_date TEXT,
      review_count INTEGER DEFAULT 0,
      created_at TEXT DEFAULT (datetime('now')),
      updated_at TEXT DEFAULT (datetime('now')),
      FOREIGN KEY (plan_id) REFERENCES study_plans(id)
    );

    CREATE TABLE IF NOT EXISTS plants (
      id TEXT PRIMARY KEY,
      plan_id TEXT NOT NULL,
      type TEXT NOT NULL,
      subject TEXT NOT NULL,
      progress INTEGER DEFAULT 0,
      created_at TEXT DEFAULT (datetime('now')),
      updated_at TEXT DEFAULT (datetime('const Database = require('better-sqlite3');
const path = require('path');

const dbPath = path.join(__dirname, 'studymate.db');
const db = new Database(dbPath);

// 启用 WAL 模式提升并发性能
db.pragma('journal_mode = WAL');
db.pragma('foreign_keys = ON');

function initDB() {
  db.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id TEXT PRIMARY KEY,
      email TEXT UNIQUE NOT NULL,
      password_hash TEXT NOT NULL,
      nickname TEXT,
      avatar_url TEXT,
      created_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS study_plans (
      id TEXT PRIMARY KEY,
      user_id TEXT NOT NULL,
      exam_name TEXT NOT NULL,
      exam_date TEXT,
      target_scores TEXT DEFAULT '{}',
      daily_study_time INTEGER DEFAULT 0,
      weak_points TEXT DEFAULT '[]',
      study_phase TEXT DEFAULT 'planning',
      notes TEXT DEFAULT '',
      ai_plan TEXT,
      created_at TEXT DEFAULT (datetime('now')),
      FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS daily_tasks (
      id TEXT PRIMARY KEY,
      plan_id TEXT NOT NULL,
      date TEXT NOT NULL,
      type TEXT NOT NULL,
      subject TEXT NOT NULL,
      content TEXT NOT NULL,
      duration INTEGER DEFAULT 0,
      status TEXT DEFAULT 'pending',
      completed_at TEXT,
      proof_image_url TEXT,
      created_at TEXT DEFAULT (datetime('now')),
      FOREIGN KEY (plan_id) REFERENCES study_plans(id)
    );

    CREATE TABLE IF NOT EXISTS flash_cards (
      id TEXT PRIMARY KEY,
      plan_id TEXT NOT NULL,
      question TEXT NOT NULL,
      answer TEXT NOT NULL,
      subject TEXT NOT NULL,
      mastery_level INTEGER DEFAULT 0,
      next_review_date TEXT,
      review_count INTEGER DEFAULT 0,
      created_at TEXT DEFAULT (datetime('now')),
      updated_at TEXT DEFAULT (datetime('now')),
      FOREIGN KEY (plan_id) REFERENCES study_plans(id)
    );

    CREATE TABLE IF NOT EXISTS plants (
      id TEXT PRIMARY KEY,
      plan_id TEXT NOT NULL,
      type TEXT NOT NULL,
      subject TEXT NOT NULL,
      progress INTEGER DEFAULT 0,
      created_at TEXT DEFAULT (datetime('now')),
      updated_at TEXT DEFAULT (datetime('now')),
      FOREIGN KEY (plan_id) REFERENCES study_plans(id)
    );