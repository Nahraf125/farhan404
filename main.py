from fastapi import  FastAPI


app = FastAPI()

data = {
    "P001": {
        "name": "Laptop",
        "price": 1000,
        "quantity": 10,
        "description": "A high-performance laptop for work and play.",
        "Brand": "hp"
    },
    "P002": {
        "name": "Smartphone",
        "price": 500,
        "quantity": 20,
        "description": "A sleek and powerful smartphone with a stunning display.",
        "Brand": "Samsung"
    }
}

@app.get("/")
def first_api():
    return {"message": "Hello, World!"}

@app.get("/about")
def second_api():
    return {"message": "I am a saylani's Student"}

@app.get("/products/{product_id}")
def get_product(product_id: str):
    return data.get(product_id)