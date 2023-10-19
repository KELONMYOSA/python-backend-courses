package auth

import (
	"context"
	"log"
	"regexp"
	"time"

	pb "go_auth/pb_auth"
	"go_auth/utils/dao"

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

// LoginUser - Проверка корректности данных и получение токена
func (s *Server) LoginUser(_ context.Context, req *pb.UserLogin) (*pb.Token, error) {
	// Проверка электронной почты пользователя и получение хеша его пароля из базы данных
	db := dao.Connect()
	user := db.GetUserByEmail(req.Email)
	db.Close()
	if user == (dao.UserInDB{}) {
		return nil, status.Error(codes.Unauthenticated, "Incorrect username or password")
	}

	// Проверка соответствия пароля
	if !verifyPassword(req.Password, user.HashedPassword) {
		return nil, status.Error(codes.Unauthenticated, "Incorrect username or password")
	}

	// Создание токена аутентификации
	accessToken, err := createAccessToken(req.Email)
	if err != nil {
		return nil, status.Error(codes.Unauthenticated, "Incorrect username or password")
	}

	log.Printf("Successful login: %v", req.Email)

	return &pb.Token{
		AccessToken: accessToken,
		TokenType:   "bearer",
	}, nil
}

// AuthUser - Проверка токена и получение данных пользователя
func (s *Server) AuthUser(_ context.Context, req *pb.Token) (*pb.UserData, error) {
	// Проверяем валидность токена
	tokenClaims := jwt.MapClaims{}
	tokenParser := jwt.Parser{ValidMethods: []string{"HS256"}}
	token, err := tokenParser.ParseWithClaims(req.AccessToken, tokenClaims, func(token *jwt.Token) (interface{}, error) {
		return []byte(secretKey), nil
	})

	if err != nil || !token.Valid {
		return nil, status.Error(codes.Unauthenticated, "Could not validate credentials")
	}

	email, ok := tokenClaims["sub"].(string)
	if !ok {
		return nil, status.Error(codes.Unauthenticated, "Could not validate credentials")
	}

	// Получаем данные пользователя
	db := dao.Connect()
	user := db.GetUserByEmail(email)
	db.Close()
	if user == (dao.UserInDB{}) {
		return nil, status.Error(codes.Unauthenticated, "Could not validate credentials")
	}

	log.Printf("Successful authorization: %v", email)

	return &pb.UserData{
		Name:  &user.Name,
		Email: user.Email,
	}, nil
}
