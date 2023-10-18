package auth

import (
	"context"
	"go_auth/utils/dao"
	"log"
	"regexp"
	"time"

	pb "go_auth/pb_auth"

	"github.com/dgrijalva/jwt-go"
	"golang.org/x/crypto/bcrypt"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
)

var (
	secretKey                = "my-secret-key"
	accessTokenExpireMinutes = 30
)

// Сравнение пароля и хэша
func verifyPassword(plainPassword string, hashedPassword string) bool {
	err := bcrypt.CompareHashAndPassword([]byte(hashedPassword), []byte(plainPassword))
	return err == nil
}

// Создание хэшированного пароля
func getPasswordHash(password string) (string, error) {
	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
	if err != nil {
		return "", err
	}
	return string(hashedPassword), nil
}

// Создание токена
func createAccessToken(email string) (string, error) {
	expire := time.Now().Add(time.Duration(accessTokenExpireMinutes) * time.Minute)
	claims := jwt.MapClaims{
		"sub": email,
		"exp": expire.Unix(),
	}
	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	tokenString, err := token.SignedString([]byte(secretKey))
	if err != nil {
		return "", err
	}
	return tokenString, nil
}

type Server struct {
	pb.UnimplementedAuthServiceServer
}

// CreateNewUser - Проверка корректности данных и создание пользователя
func (s *Server) CreateNewUser(_ context.Context, req *pb.UserReg) (*pb.Token, error) {
	// Проверка валидности электронной почты
	if !regexp.MustCompile(`[^@]+@[^@]+\.[^@]+`).MatchString(req.Email) {
		return nil, status.Error(codes.InvalidArgument, "Email validation error")
	}

	// Проверка, что пользователь с указанной электронной почтой не существует
	db := dao.Connect()
	emails := db.GetUsersEmail()
	found := false
	for _, email := range emails {
		if email == req.Email {
			found = true
			break
		}
	}
	if found {
		return nil, status.Error(codes.AlreadyExists, "A user with this email already exists")
	}

	// Проверка, что пароль содержит символы
	if len(req.Password) == 0 {
		return nil, status.Error(codes.InvalidArgument, "The password cannot be empty")
	}

	// Хеширование пароля
	hashedPassword, err := getPasswordHash(req.Password)
	if err != nil {
		return nil, status.Error(codes.InvalidArgument, "Invalid password")
	}

	// Записываем пользователя в БД
	db.SetUser(req, hashedPassword)
	db.Close()

	// Создание токена аутентификации
	accessToken, err := createAccessToken(req.Email)
	if err != nil {
		return nil, status.Error(codes.InvalidArgument, "Invalid email")
	}

	log.Printf("Successful registration: %v", req.Email)

	return &pb.Token{
		AccessToken: accessToken,
		TokenType:   "bearer",
	}, nil
}
