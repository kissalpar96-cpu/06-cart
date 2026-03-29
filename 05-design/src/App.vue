<template>
  <main class="page">
    <section class="panel">
      <header class="panel-header">
        <h1 class="panel-title">Product Management</h1>
        <div class="toolbar">
          <label class="search" aria-label="Search products">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6">
              <circle cx="11" cy="11" r="6.5" />
              <path d="M16.5 16.5L21 21" />
            </svg>
            <input type="text" placeholder="Search products..." v-model="search" />
          </label>
          <button class="btn btn-primary" type="button" @click="openCreate">
            <span>Add Product</span>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 5v14" />
              <path d="M5 12h14" />
            </svg>
          </button>
        </div>
      </header>

      <div class="grid">
        <article v-for="product in filteredProducts" :key="product.id" class="card">
                    <div class="card-actions">
            <button class="btn" type="button" @click="openDetails(product)">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                <path d="M2 12s4-6 10-6 10 6 10 6-4 6-10 6-10-6-10-6Z" />
                <circle cx="12" cy="12" r="3" />
              </svg>
              <span>View</span>
            </button>
            <button class="btn" type="button" @click="openEdit(product)">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                <path d="M4 20h4l10-10-4-4L4 16v4Z" />
                <path d="M14 6l4 4" />
              </svg>
              <span>Edit</span>
            </button>
            <button class="btn btn-cart" type="button" :disabled="product.stock <= 0" @click="addToCart(product)">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 5v14" />
                <path d="M5 12h14" />
              </svg>
              <span>Add</span>
            </button>
            <button class="btn btn-danger" type="button" aria-label="Delete" @click="openDelete(product)">
              <svg viewBox="0 0 24 24" fill="none" stroke-width="1.8">
                <path d="M3 6h18" />
                <path d="M8 6V4h8v2" />
                <path d="M19 6l-1 14H6L5 6" />
              </svg>
            </button>
          </div>

          <h2 class="card-title">{{ product.name }}</h2>
          <p class="card-desc">{{ product.description }}</p>
          <div class="card-meta">
            <span>Stock: {{ product.stock }}</span>
            <span class="price">${{ product.price }}</span>
          </div>
        </article>
      </div>
    </section>
  </main>

  <aside class="cart" aria-live="polite">
    <header class="cart-header">
      <h2 class="cart-title">Cart</h2>
      <span class="cart-count">{{ cartCount }} items</span>
    </header>
    <p v-if="cartNotice" class="cart-notice">{{ cartNotice }}</p>
    <ul v-if="cartItems.length" class="cart-list">
      <li v-for="item in cartItems" :key="item.product_id" class="cart-item">
        <div>
          <span class="cart-name">{{ item.name }}</span>
          <span class="cart-qty">x{{ item.quantity }}</span>
        </div>
        <div class="cart-actions">
          <span class="cart-price">${{ (item.price * item.quantity).toFixed(2) }}</span>
          <button class="cart-remove" type="button" @click="removeFromCart(item.product_id)">
            -
          </button>
        </div>
      </li>
    </ul>
    <p v-else class="cart-empty">Cart is empty</p>
    <div class="cart-total">
      <span>Total</span>
      <span>${{ cartTotal.toFixed(2) }}</span>
    </div>
  </aside>
  <div v-if="showCreateDialog" class="dialog-backdrop" @click.self="closeCreate">
    <div class="dialog" role="dialog" aria-modal="true" aria-labelledby="dialog-create-title">
      <button class="dialog-close" type="button" aria-label="Close" @click="closeCreate">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M6 6l12 12" />
          <path d="M18 6L6 18" />
        </svg>
      </button>
      <h2 id="dialog-create-title" class="dialog-title">Add New Product</h2>
      <form class="dialog-form" @submit.prevent="createProduct">
        <label class="field">
          <span>Product Name</span>
          <input type="text" placeholder="Enter product name" v-model="createForm.name" required />
        </label>
        <label class="field">
          <span>Description</span>
          <textarea rows="3" placeholder="Enter product description" v-model="createForm.description" required></textarea>
        </label>
        <div class="field-row">
          <label class="field">
            <span>Price ($)</span>
            <input type="number" step="0.01" min="0" placeholder="0.00" v-model="createForm.price" required />
          </label>
          <label class="field">
            <span>Stock</span>
            <input type="number" min="0" placeholder="0" v-model="createForm.stock" required />
          </label>
        </div>
        <div class="dialog-actions">
          <button class="btn btn-ghost" type="button" @click="closeCreate">Cancel</button>
          <button class="btn btn-primary" type="submit">Add Product</button>
        </div>
      </form>
    </div>
  </div>

  <div v-if="showEditDialog" class="dialog-backdrop" @click.self="closeEdit">
    <div class="dialog" role="dialog" aria-modal="true" aria-labelledby="dialog-edit-title">
      <button class="dialog-close" type="button" aria-label="Close" @click="closeEdit">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M6 6l12 12" />
          <path d="M18 6L6 18" />
        </svg>
      </button>
      <h2 id="dialog-edit-title" class="dialog-title">Edit Product</h2>
      <form class="dialog-form" @submit.prevent="updateProduct">
        <label class="field">
          <span>Product Name</span>
          <input type="text" v-model="editForm.name" required />
        </label>
        <label class="field">
          <span>Description</span>
          <textarea rows="4" v-model="editForm.description" required></textarea>
        </label>
        <div class="field-row">
          <label class="field">
            <span>Price ($)</span>
            <input type="number" step="0.01" min="0" v-model="editForm.price" required />
          </label>
          <label class="field">
            <span>Stock</span>
            <input type="number" min="0" v-model="editForm.stock" required />
          </label>
        </div>
        <div class="dialog-actions">
          <button class="btn btn-ghost" type="button" @click="closeEdit">Cancel</button>
          <button class="btn btn-primary" type="submit">Update Product</button>
        </div>
      </form>
    </div>
  </div>

  <div v-if="showDetailsDialog" class="dialog-backdrop" @click.self="showDetailsDialog = false">
    <div class="dialog dialog-details" role="dialog" aria-modal="true" aria-labelledby="dialog-details-title">
      <button class="dialog-close" type="button" aria-label="Close" @click="showDetailsDialog = false">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M6 6l12 12" />
          <path d="M18 6L6 18" />
        </svg>
      </button>
      <h2 id="dialog-details-title" class="dialog-title">Product Details</h2>
      <h3 class="details-name">{{ detailsProduct.name }}</h3>
      <p class="details-description">{{ detailsProduct.description }}</p>
      <div class="details-divider"></div>
      <div class="details-meta">
        <div>
          <span class="details-label">Price:</span>
          <span class="details-value">$ {{ detailsProduct.price }}</span>
        </div>
        <div>
          <span class="details-label">Stock:</span>
          <span class="details-value">{{ detailsProduct.stock }} units</span>
        </div>
        <div>
          <span class="details-label">Product ID:</span>
          <span class="details-id">{{ detailsProduct.id }}</span>
        </div>
      </div>
    </div>
  </div>

  <div v-if="showDeleteDialog" class="dialog-backdrop" @click.self="closeDelete">
    <div class="dialog dialog-delete" role="dialog" aria-modal="true" aria-labelledby="dialog-delete-title">
      <h2 id="dialog-delete-title" class="dialog-title">Delete Product</h2>
      <p class="delete-message">
        Are you sure you want to delete "{{ deleteTarget?.name }}"? This action cannot be undone.
      </p>
      <div class="dialog-actions dialog-actions-delete">
        <button class="btn btn-ghost" type="button" @click="closeDelete">Cancel</button>
        <button class="btn btn-danger btn-delete" type="button" @click="deleteProduct">Delete Product</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue'

type Product = {
  id: number
  name: string
  description: string
  stock: number
  price: number
}

type CartItem = {
  product_id: number
  name: string
  price: number
  quantity: number
}

const API_BASE = 'http://localhost:8000/products'
const CART_BASE = 'http://localhost:8000/cart'

const products = ref<Product[]>([])
const cartItems = ref<CartItem[]>([])
const cartNotice = ref('')
const search = ref('')

const showCreateDialog = ref(false)
const showEditDialog = ref(false)
const showDetailsDialog = ref(false)
const showDeleteDialog = ref(false)

const createForm = reactive({
  name: '',
  description: '',
  price: '',
  stock: '',
})

const editForm = reactive({
  id: 0,
  name: '',
  description: '',
  price: '',
  stock: '',
})

const detailsProduct = reactive<Product>({
  id: 0,
  name: '',
  description: '',
  stock: 0,
  price: 0,
})

const deleteTarget = ref<Product | null>(null)

const filteredProducts = computed(() => {
  const term = search.value.trim().toLowerCase()
  if (!term) return products.value
  return products.value.filter((product) =>
    [product.name, product.description].some((field) => field.toLowerCase().includes(term))
  )
})

const cartCount = computed(() =>
  cartItems.value.reduce((total, item) => total + item.quantity, 0)
)

const cartTotal = computed(() =>
  cartItems.value.reduce((total, item) => total + item.price * item.quantity, 0)
)

const fetchProducts = async () => {
  const response = await fetch(API_BASE)
  if (!response.ok) {
    throw new Error('Failed to load products')
  }
  const data = (await response.json()) as Product[]
  products.value = data
}

const fetchCart = async () => {
  const response = await fetch(CART_BASE)
  if (!response.ok) {
    throw new Error('Failed to load cart')
  }
  const data = (await response.json()) as CartItem[]
  cartItems.value = data
}

const addToCart = async (product: Product) => {
  if (product.stock <= 0) {
    cartNotice.value = 'Out of stock'
    return
  }
  cartNotice.value = ''
  const response = await fetch(`${CART_BASE}/add`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ product_id: product.id }),
  })
  if (!response.ok) {
    const data = await response.json().catch(() => null)
    cartNotice.value = data?.detail ?? 'Failed to add to cart'
    return
  }
  await Promise.all([fetchProducts(), fetchCart()])
}

const removeFromCart = async (productId: number) => {
  cartNotice.value = ''
  const response = await fetch(`${CART_BASE}/remove`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ product_id: productId }),
  })
  if (!response.ok) {
    const data = await response.json().catch(() => null)
    cartNotice.value = data?.detail ?? 'Failed to remove from cart'
    return
  }
  await Promise.all([fetchProducts(), fetchCart()])
}

fetchProducts().catch((error) => {
  console.error(error)
})

fetchCart().catch((error) => {
  console.error(error)
})

const openCreate = () => {
  createForm.name = ''
  createForm.description = ''
  createForm.price = ''
  createForm.stock = ''
  showCreateDialog.value = true
}

const closeCreate = () => {
  showCreateDialog.value = false
}

const closeEdit = () => {
  showEditDialog.value = false
}

const closeDelete = () => {
  showDeleteDialog.value = false
  deleteTarget.value = null
}

const openEdit = (product: Product) => {
  editForm.id = product.id
  editForm.name = product.name
  editForm.description = product.description
  editForm.price = String(product.price)
  editForm.stock = String(product.stock)
  showEditDialog.value = true
}

const openDetails = (product: Product) => {
  detailsProduct.id = product.id
  detailsProduct.name = product.name
  detailsProduct.description = product.description
  detailsProduct.stock = product.stock
  detailsProduct.price = product.price
  showDetailsDialog.value = true
}

const openDelete = (product: Product) => {
  deleteTarget.value = product
  showDeleteDialog.value = true
}

const createProduct = async () => {
  const payload = {
    name: createForm.name.trim(),
    description: createForm.description.trim(),
    price: Number(createForm.price),
    stock: Number(createForm.stock),
  }
  const response = await fetch(API_BASE, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!response.ok) {
    throw new Error('Failed to create product')
  }
  await Promise.all([fetchProducts(), fetchCart()])
  closeCreate()
}

const updateProduct = async () => {
  const payload = {
    name: editForm.name.trim(),
    description: editForm.description.trim(),
    price: Number(editForm.price),
    stock: Number(editForm.stock),
  }
  const response = await fetch(`${API_BASE}/${editForm.id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!response.ok) {
    throw new Error('Failed to update product')
  }
  await Promise.all([fetchProducts(), fetchCart()])
  closeEdit()
}

const deleteProduct = async () => {
  if (!deleteTarget.value) return
  const response = await fetch(`${API_BASE}/${deleteTarget.value.id}`, {
    method: 'DELETE',
  })
  if (!response.ok) {
    throw new Error('Failed to delete product')
  }
  await Promise.all([fetchProducts(), fetchCart()])
  closeDelete()
}
</script>

















