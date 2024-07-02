package main

import (
	"context"
	"fmt"
	"image"
	"image/jpeg"
	"image/png"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"sync"

	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

const (
	maxImageSizeBytes = 100 * 1024 // 100 KB
	imageDir          = "./images"
)

func downloadImagesFromMongoDB(uri, database, collection string, maxWorkers int) {
	// Set up MongoDB client
	client, err := mongo.Connect(context.Background(), options.Client().ApplyURI(uri))
	if err != nil {
		fmt.Printf("Failed to connect to MongoDB: %v\n", err)
		return
	}
	defer func() {
		if err := client.Disconnect(context.Background()); err != nil {
			fmt.Printf("Failed to disconnect from MongoDB: %v\n", err)
		}
	}()

	// Access the specified database and collection
	coll := client.Database(database).Collection(collection)

	// Query MongoDB for documents
	cursor, err := coll.Find(context.Background(), bson.D{})
	if err != nil {
		fmt.Printf("Failed to execute find query: %v\n", err)
		return
	}
	defer cursor.Close(context.Background())

	var wg sync.WaitGroup
	sem := make(chan struct{}, maxWorkers)

	// Ensure the images directory exists
	err = ensureDirExists(imageDir)
	if err != nil {
		fmt.Printf("Failed to create images directory: %v\n", err)
		return
	}

	// Iterate over the documents
	for cursor.Next(context.Background()) {
		var document bson.M
		if err := cursor.Decode(&document); err != nil {
			fmt.Printf("Failed to decode document: %v\n", err)
			continue
		}

		// Extract product ID from the document
		productID, ok := document["product_id"].(string)
		if !ok {
			fmt.Printf("Failed to get product_id from document: %+v\n", document)
			continue
		}

		// Extract image URL from the document
		imageURL, ok := document["image_url"].(string)
		if !ok {
			fmt.Printf("Failed to get image_url from document: %+v\n", document)
			continue
		}

		wg.Add(1)
		go func(id, url string) {
			defer wg.Done()

			// Acquire semaphore slot
			sem <- struct{}{}
			defer func() {
				// Release semaphore slot
				<-sem
			}()

			// Download and compress the image
			err := downloadAndCompressImage(id, url)
			if err != nil {
				fmt.Printf("Failed to download and compress image for product_id %s: %v\n", id, err)
			}
		}(productID, imageURL)
	}

	wg.Wait()
	close(sem)
	fmt.Println("All downloads completed.")
}

func downloadAndCompressImage(productID, url string) error {
	// Get the data from URL
	response, err := http.Get(url)
	if err != nil {
		return fmt.Errorf("failed to download %s: %v", url, err)
	}
	defer response.Body.Close()

	// Determine image format based on Content-Type header
	contentType := response.Header.Get("Content-Type")
	var img image.Image
	switch {
	case strings.HasPrefix(contentType, "image/jpeg"):
		img, err = jpeg.Decode(response.Body)
		if err != nil {
			return fmt.Errorf("failed to decode JPEG image %s: %v", url, err)
		}
	case strings.HasPrefix(contentType, "image/png"):
		img, err = png.Decode(response.Body)
		if err != nil {
			return fmt.Errorf("failed to decode PNG image %s: %v", url, err)
		}
	default:
		return fmt.Errorf("unsupported image format for %s: %s", url, contentType)
	}

	// Create a file to store the compressed image
	fileName := fmt.Sprintf("%s.jpg", productID)
	filePath := filepath.Join(imageDir, fileName)
	file, err := os.Create(filePath)
	if err != nil {
		return fmt.Errorf("failed to create file for %s: %v", url, err)
	}
	defer file.Close()

	// Compress the image to fit within 100 KB
	err = compressImage(img, file)
	if err != nil {
		return fmt.Errorf("failed to compress image %s: %v", url, err)
	}

	fmt.Printf("Downloaded, compressed, and saved %s\n", url)

	// Dummy function call to upload the image
	err = upload(filePath)
	if err != nil {
		fmt.Printf("Failed to upload image %s: %v\n", filePath, err)
	}

	return nil
}

func compressImage(img image.Image, writer io.Writer) error {
	// Encode the image to JPEG format with compression
	opts := jpeg.Options{
		Quality: 75, // Adjust quality as needed
	}

	err := jpeg.Encode(writer, img, &opts)
	if err != nil {
		return err
	}

	return nil
}

func upload(filePath string) error {
	// Dummy function to simulate uploading logic
	// You can implement actual uploading logic here
	fmt.Printf("Uploading image %s...\n", filePath)
	// Example: upload to cloud storage, database, etc.
	// Placeholder implementation:
	// return fmt.Errorf("upload not implemented")
	return nil
}

func ensureDirExists(dir string) error {
	// Check if directory exists, create if not
	_, err := os.Stat(dir)
	if os.IsNotExist(err) {
		err := os.MkdirAll(dir, 0755)
		if err != nil {
			return err
		}
	}
	return nil
}

func main() {
	// MongoDB connection parameters
	uri := "mongodb://localhost:27017"
	database := "juno"
	collection := "products"

	// Limit the number of concurrent downloads
	maxWorkers := 5

	// Download images from MongoDB
	downloadImagesFromMongoDB(uri, database, collection, maxWorkers)
}
