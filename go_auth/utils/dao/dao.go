package dao

import (
	pb "go_auth/pb_auth"

	"database/sql"
	_ "github.com/mattn/go-sqlite3"
)

type Database struct {
	db *sql.DB
}

// Connect - Устанавливаем соединение с базой данных
func Connect() *Database {
	const dbLocation = "../database/database.sqlite"
	db, err := sql.Open("sqlite3", dbLocation)
	if err != nil {
		panic(err)
	}
	return &Database{db}
}

// Close - Закрываем соединение
func (d *Database) Close() {
	err := d.db.Close()
	if err != nil {
		return
	}
}

// GetUsersEmail - Получение всех email пользователей
func (d *Database) GetUsersEmail() []string {
	rows, err := d.db.Query("SELECT email FROM user")
	if err != nil {
		return nil
	}
	defer rows.Close()

	var emails []string
	for rows.Next() {
		var email string
		if err := rows.Scan(&email); err != nil {
			return nil
		}
		emails = append(emails, email)
	}

	return emails
}

// SetUser - Создание нового пользователя
func (d *Database) SetUser(user *pb.UserReg, hashedPassword string) {
	_, err := d.db.Exec("INSERT INTO user (name, email, password) VALUES (?, ?, ?)",
		user.Name, user.Email, hashedPassword)
	if err != nil {
		panic(err)
	}
}

type UserInDB struct {
	Name           string
	Email          string
	HashedPassword string
}

// GetUserByEmail - Получаем данные пользователя по email
func (d *Database) GetUserByEmail(email string) UserInDB {
	row := d.db.QueryRow("SELECT name, email, password FROM user WHERE email = ?", email)

	var name, hashedPassword string
	err := row.Scan(&name, &email, &hashedPassword)
	if err != nil {
		return UserInDB{}
	}

	return UserInDB{Name: name, Email: email, HashedPassword: hashedPassword}
}
