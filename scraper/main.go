package main

import (
	"context"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"time"
	"regexp"
	"strconv"
	"strings"
	"github.com/google/uuid"


	"github.com/PuerkitoBio/goquery"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

type Product struct {
	ProductID     string   `bson:"product_id"`
	ProductURL    string   `bson:"product_url"`
	ShopifyID     string   `bson:"shopify_id"`
	Handle        string   `bson:"handle"`
	Title         string   `bson:"title"`
	Vendor        string   `bson:"vendor"`
	VendorTitle   string   `bson:"vendor_title"`
	Category      string   `bson:"category"`
	ProductType   string   `bson:"product_type"`
	ImageURL      string   `bson:"image_url"`
	Images        []string `bson:"images"`
	Description   string   `bson:"description"`
	Price         int      `bson:"price"`
	ComparePrice  int      `bson:"compare_price"`
	Discount      int      `bson:"discount"`
	Currency      string   `bson:"currency"`
	Variants      []Variant `bson:"variants"`
	Options       []ShopifyOption  `bson:"options"`
	Tags          []string  `bson:"tags"`
	Available     bool     `bson:"available"`
}


type Variant struct {
	ID            string `bson:"id"`
	Price         int    `bson:"price"`
	Title         string `bson:"title"`
	ComparePrice  int    `bson:"compare_price"`
	Available 	  bool 	 `bson:"available"`
	Option1       string `bson:"option1"`
	Option2       string `bson:"option2"`
	Option3       string `bson:"option3"`
}


type Brand struct {
	Name    string `json:"name"`
	BaseURL string `json:"base_url"`
}


type ShopifyProduct struct {
	ID           int64     `json:"id" bson:"id"`
	Title        string    `json:"title" bson:"title"`
	Handle       string    `json:"handle" bson:"handle"`
	BodyHTML     string    `json:"body_html" bson:"body_html"`
	PublishedAt  time.Time `json:"published_at" bson:"published_at"`
	CreatedAt    time.Time `json:"created_at" bson:"created_at"`
	UpdatedAt    time.Time `json:"updated_at" bson:"updated_at"`
	Vendor       string    `json:"vendor" bson:"vendor"`
	ProductType  string    `json:"product_type" bson:"product_type"`
	Tags         []string  `json:"tags" bson:"tags"`
	Variants     []Variant `json:"variants" bson:"variants"`
	Images       []ShopifyImage   `json:"images" bson:"images"`
	Options      []ShopifyOption  `json:"options" bson:"options"`
}

type ShopifyVariant struct {
	ID                int64     `json:"id" bson:"id"`
	Title             string    `json:"title" bson:"title"`
	Option1           string    `json:"option1" bson:"option1"`
	Option2           string    `json:"option2" bson:"option2"`
	Option3           string    `json:"option3" bson:"option3"`
	SKU               string    `json:"sku" bson:"sku"`
	RequiresShipping  bool      `json:"requires_shipping" bson:"requires_shipping"`
	Taxable           bool      `json:"taxable" bson:"taxable"`
	FeaturedImage     string    `json:"featured_image" bson:"featured_image"`
	Available         bool      `json:"available" bson:"available"`
	Price             string    `json:"price" bson:"price"`
	Grams             int       `json:"grams" bson:"grams"`
	CompareAtPrice    string    `json:"compare_at_price" bson:"compare_at_price"`
	Position          int       `json:"position" bson:"position"`
	ProductID         int64     `json:"product_id" bson:"product_id"`
	CreatedAt         time.Time `json:"created_at" bson:"created_at"`
	UpdatedAt         time.Time `json:"updated_at" bson:"updated_at"`
}

type ShopifyImage struct {
	ID         int64     `json:"id" bson:"id"`
	CreatedAt  time.Time `json:"created_at" bson:"created_at"`
	Position   int       `json:"position" bson:"position"`
	UpdatedAt  time.Time `json:"updated_at" bson:"updated_at"`
	ProductID  int64     `json:"product_id" bson:"product_id"`
	VariantIDs []int64   `json:"variant_ids" bson:"variant_ids"`
	Src        string    `json:"src" bson:"src"`
	Width      int       `json:"width" bson:"width"`
	Height     int       `json:"height" bson:"height"`
}

type ShopifyOption struct {
	Name     string   `json:"name" bson:"name"`
	Position int      `json:"position" bson:"position"`
	Values   []string `json:"values" bson:"values"`
}

var brands = []Brand{
	{"afrozeh", "https://www.afrozeh.com"},
	{"ali_xeeshan", "https://alixeeshanempire.com"},
	{"alkaram_studio", "https://www.alkaramstudio.com"},
	{"asim_jofa", "https://asimjofa.com"},
	{"beechtree", "https://beechtree.pk"},
	{"bonanza_satrangi", "https://bonanzasatrangi.com"},
	{"chinyere", "https://chinyere.pk"},
	{"cross_stitch", "https://www.crossstitch.pk"},
	{"edenrobe", "https://edenrobe.com"},
	{"ethnic", "https://pk.ethnc.com"},
	{"faiza_saqlain", "https://www.faizasaqlain.pk"},
	{"generation", "https://generation.com.pk"},
	{"hem_stitch", "https://www.hemstitch.pk"},
	{"hussain_rehar", "https://www.hussainrehar.com"},
	{"kanwal_malik", "https://www.kanwalmalik.com"},
	{"kayseria", "https://www.kayseria.com"},
	{"limelight", "https://www.limelight.pk"},
	{"maria_b", "https://www.mariab.pk"},
	{"mushq", "https://www.mushq.pk"},
	{"nishat_linen", "https://nishatlinen.com"},
	{"sadaf_fawad_khan", "https://sadaffawadkhan.com"},
	{"sapphire", "https://pk.sapphireonline.pk"},
	{"zaha", "https://www.zaha.pk"},
	{"zara_shah_jahan", "https://zarashahjahan.com"},
	{"zellbury", "https://zellbury.com"},
	{"outfitters", "https://outfitters.com.pk"},
	{"breakout", "https://breakout.com.pk"},
	{"azure", "https://www.azureofficial.pk"},
	{"almirah", "https://almirah.com.pk"},
	{"saya", "https://saya.pk"},
	{"senorita", "https://senorita.pk"},
	{"zeen", "https://zeenwoman.com"},
	{"mahum_asad", "https://mahumasad.com"},
	{"mohagni", "https://mohagni.com"},
	{"adans_libas", "https://www.adanslibas.com"},
	{"iznik", "https://iznikfashions.com"},
	{"ammara_khan", "https://www.ammarakhan.com"},
	{"alizeh", "https://alizeh.pk"},
	{"vanya", "https://vanya.pk/"},
	{"so_kamal", "https://sokamal.com"},
	{"baroque", "https://baroque.pk"},
	{"rafia", "https://rafia.pk"},
	{"motifz", "https://motifz.com.pk"},
	{"anaya", "https://anayaonline.com"},
}

var mongoURI = "mongodb://localhost:27017/"
var databaseName = "juno"
var collectionName = "products"
var collection *mongo.Collection

func main() {
	clientOptions := options.Client().ApplyURI(mongoURI)
	client, err := mongo.Connect(context.TODO(), clientOptions)
	if err != nil {
		log.Fatal(err)
	}
	defer client.Disconnect(context.TODO())

	db := client.Database(databaseName)
	collection = db.Collection(collectionName, options.Collection())
	fmt.Printf("Total brands = %d\n", len(brands))

	for _, brand := range brands {
		name := strings.Replace(brand.Name, "_", " ", -1)
		brand.Name = name
		scrapeBrand(collection, brand)
	}
}

func scrapeBrand(collection *mongo.Collection, brand Brand) {
	baseURL := brand.BaseURL
	name := brand.Name
	handle := strings.ToLower(strings.Replace(name, " ", "_", -1))

	url := fmt.Sprintf("%s/products.json", baseURL)
	page := 1

	products := getPage(baseURL, url, handle, page, true, collection)
	for len(products) > 0 {
		page++
		products = getPage(baseURL, url, handle, page, true, collection)
	}

	fmt.Printf("Total new products scraped = %d, from %s\n", len(products), brand.Name)
}

func getPage(baseURL, url, handle string, page int, upload bool, collection *mongo.Collection) []Product {
	response, err := http.Get(fmt.Sprintf("%s?page=%d", url, page))
	if err != nil {
		log.Fatal(err)
	}
	defer response.Body.Close()

	body, err := ioutil.ReadAll(response.Body)
	if err != nil {
		log.Fatal(err)
	}

	var result map[string][]ShopifyProduct
	json.Unmarshal(body, &result)


	products := result["products"]
	extractedProducts := []Product{}
	for _, product := range products {
		extractedProduct := extractFields(baseURL, handle, product)
		if extractedProduct != nil {
			extractedProducts = append(extractedProducts, *extractedProduct)
			if upload {
				uploadToMongo(collection, extractedProduct)
			}
		}
	}

	log.Println("extracted products = " , extractedProducts)

	return extractedProducts
}

func extractFields(baseURL, handle string, product ShopifyProduct) *Product {
	if product.BodyHTML == "" {
		return nil
	}

	description := preprocessText(product.BodyHTML)

	productAvailable := false
	variantIndex := 0
	distance := 900000000000
	comparePriceVT := -1

	for idx, variant := range product.Variants {
		price := variant.Price
		comparePrice := variant.ComparePrice

		if price == 0 {
			price = 500
			comparePrice = 500
		}

		if variant.Available {
			thisDistance := abs(1000 - price)
			if thisDistance < distance {
				distance = thisDistance
				variantIndex = idx
				comparePriceVT = comparePrice
			}
			productAvailable = true
		}
	}

	if !productAvailable {
		return nil
	}

	variant := product.Variants[variantIndex]
	url := fmt.Sprintf("%s/products/%s", baseURL, product.Handle)
	price := variant.Price
	images := product.Images
	if len(images) == 0 {
		return nil
	}

	imageURL := images[0]
	imageURLs := []string{}
	for _,  image := range images {
		imageURLs = append(imageURLs, image.Src)
	}

	if price < 100 {
		price = 500
		comparePriceVT = 500
	}

	discount := 0
	if comparePriceVT != -1 && comparePriceVT != 0 && price != 0 {
		res := 1 - (float64(price) / float64(comparePriceVT))
		if res < 0.1 && res > 0 {
			res = 0.1
		}
		if res > 0 {
			discount = int(res * 100)
		}
	}



	newProduct := &Product{
		ProductID:     uuid.New().String(),
		ProductURL:    url,
		ShopifyID:     strconv.Itoa(int(product.ID)),
		Handle:        product.Handle,
		Title:         strings.Title(strings.Replace(product.Title, "-", " ", -1)),
		Vendor:        handle,
		VendorTitle:   strings.Title(strings.Replace(handle, "_", " ", -1)),
		Category:      "",
		ProductType:   product.ProductType,
		ImageURL:      imageURL.Src,
		Images:        imageURLs,
		Description:   description,
		Price:         price,
		ComparePrice:  comparePriceVT,
		Discount:      discount,
		Currency:      "PKR",
		Variants:      product.Variants,
		Options:       product.Options,
				Tags:          product.Tags,
		Available:     productAvailable,
	}

	// if exists just update
	exists := updateProductIfExists(collection, newProduct)
	if exists {
		return nil
	}

	return newProduct
}

func uploadToMongo(collection *mongo.Collection, product *Product) {
	_, err := collection.InsertOne(context.TODO(), product)
	if err != nil {
		log.Printf("Failed to upload product to MongoDB: %v", err)
	}
}

func updateProductIfExists(collection *mongo.Collection, product *Product) bool {
	filter := bson.M{"shopify_id": product.ShopifyID}
	update := bson.M{"$set": bson.M{"available" : product.Available}}

	result := collection.FindOneAndUpdate(context.TODO(), filter, update, options.FindOneAndUpdate().SetReturnDocument(options.After))
	if result.Err() != nil {
		if result.Err() == mongo.ErrNoDocuments {
			return false
		}
		log.Printf("Error checking existing product: %v", result.Err())
		return false
	}

	var updatedProduct Product
	err := result.Decode(&updatedProduct)
	if err != nil {
		log.Printf("Failed to decode updated product: %v", err)
		return false
	}

	product.ProductID = updatedProduct.ProductID
	return true
}

func preprocessText(text string) string {
	text = removeUnicodeCodes(text)
	text = removeHTMLTags(text)
	return text
}

func removeUnicodeCodes(text string) string {
	re := regexp.MustCompile(`\\u[0-9a-fA-F]{4}`)
	return re.ReplaceAllString(text, "")
}

func removeHTMLTags(text string) string {
	doc, err := goquery.NewDocumentFromReader(strings.NewReader(text))
	if err != nil {
		log.Printf("Failed to parse HTML: %v", err)
		return text
	}
	return doc.Text()
}

func abs(x int) int {
	if x < 0 {
		return -x
	}
	return x
}
