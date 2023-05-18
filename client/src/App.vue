<template>
	<div class="container">
		<div class="left-pane">
			<div class="lookup-area">
				<input v-model="searchTerm" placeholder="Search…" @input="searchTermChanged">
				<ul>
					<li v-for="word in wordList"
						:key="word.fakeID"
						@click="search(word)">
						{{ word }}
					</li>
				</ul>

			</div>
			<div class="history-area">
				<p id="history-heading">
					<strong>Search History</strong> ({{ searchHistory.length }}/{{ historySize }})
					<button @click="searchHistory = []">Clear</button> <!-- If search history is cleared, it won't be immediately synced with the backend. Not a bug, but a feature. -->
					<button @click="getHistory">Export JSON</button>
				</p>
				<ul>
					<li v-for="entry in searchHistory"
						:key="entry"
						@click="search(entry)">
						{{ entry }}
					</li>
				</ul>
			</div>
		</div>
		<div class="middle-pane">
			<div v-html="definition"></div>
		</div>
		<div class="right-pane">
			<p id="dictionaries-heading">
				<strong>Dictionaries</strong>&nbsp;
				<button @click="showAddDictionaryDialogue = !showAddDictionaryDialogue">+</button>
				<button @click="showSettingsDialogue = !showSettingsDialogue">Settings</button>
			</p>
			<ul>
				<li v-for="dictionary in dictionaries"
					:key="dictionary"
					@click="activeDictionaryChanged(dictionary)"
					:class="{ active: activeDictionary['name'] == dictionary['name']}">
					{{ dictionary.displayName }}
				</li>
			</ul>
		</div>
		<div v-if="showSettingsDialogue" class="dialogue">
			<label><strong>History Size (&leqslant; 0 to disable):</strong></label>
			<input v-model="historySize" @input="historySizeChanged">
			<label><strong>Dictionaries (drag and drop to reorder):</strong></label>
			<ul>
				<li v-for="(dictionary, index) in dictionaries"
					:key="dictionary"
					draggable="true"
					@dragstart="dragStart(index)"
					@dragover="dragOver(index)"
					@drop="drop(index)">
					<button @click="editedDictionary = dictionary; editedDictionaryDisplayName = dictionary['displayName']">✎</button>
					<button @click="deleteDictionary(dictionary)">✕</button>
					{{ dictionary.displayName }}
				</li>
			</ul>
		</div>
		<div v-if="showAddDictionaryDialogue" class="dialogue">
			<label><strong>Dictionary name</strong></label>
			<input v-model="newDictionaryDisplayName">
			<label><strong>File name</strong></label>
			<input v-model="newDictionaryFilename">
			<label><strong>Format</strong>&nbsp;</label>
			<select v-model="newDictionaryFormat">
				<option v-for="format in dictionaryFormats" :value="format" :key="format">{{ format }}</option>
			</select>&nbsp;
			<button @click="addDictionary">Add</button>
		</div>
		<div v-if="validationError" class="dialogue">
			<p>{{ validationError }}</p>
			<button @click="validationError = ''">OK</button>
		</div>
		<div v-if="editedDictionary['name']" class="dialogue">
			<label><strong>Dictionary name</strong></label>
			<input v-model="editedDictionaryDisplayName">
			<button @click="commitNameChange">OK</button>
		</div>
	</div>
</template>

<script>
import { ref } from 'vue'

const SERVER_URL = 'http://localhost:2628'
// const SERVER_URL = 'https://www.example.xyz:443'


export default {
	name: 'DictionaryApp',

	setup() {
		const searchTerm = ref('')
		const wordList = ref(['', '', '', '', '', '', '', '', '', ''])
		const searchHistory = ref([])
		const historySize = ref(100)
		const definition = ref('')
		const activeDictionary = ref({
			displayName: 'display name',
			name: 'en'
		})
		const dictionaries = ref([])
		const showSettingsDialogue = ref(false)
		const lookupCrossRefHandled = ref(false)
		const showAddDictionaryDialogue = ref(false)
		const dictionaryFormats = ref([])
		const newDictionaryDisplayName = ref('')
		const newDictionaryFilename = ref('')
		const newDictionaryFormat = ref('')
		const validationError = ref('')
		const editedDictionary = ref({})
		const editedDictionaryDisplayName = ref('')

		// Fetch dictionary list
		fetch(`${SERVER_URL}/api/metadata/dictionary_list`)
			.then((response) => response.json())
			.then((data) => {
				dictionaries.value = data.map((dictionary) => {
					return {
						displayName: dictionary.dictionary_display_name,
						name: dictionary.dictionary_name,
						format: dictionary.dictionary_format,
						filename: dictionary.dictionary_filename
					}
				},
				activeDictionary.value = data.map((dictionary) => {
					return {
						displayName: dictionary.dictionary_display_name,
						name: dictionary.dictionary_name
					}
				})[0]
				)
			})
		
		// Fetch lookup history list
		fetch(`${SERVER_URL}/api/metadata/history`)
			.then((response) => response.json())
			.then((data) => {
				searchHistory.value = data
			})

		// Fetch history size setting
		fetch(`${SERVER_URL}/api/metadata/history_size`)
			.then((response) => response.json())
			.then((data) => {
				historySize.value = data['history_size']
			})

		// Fetch dictionary formats
		fetch(`${SERVER_URL}/api/metadata/supported_dictionary_formats`)
			.then((response) => response.json())
			.then((data) => {
				dictionaryFormats.value = data
			})

		return {
			searchTerm,
			wordList,
			historySize,
			searchHistory,
			definition,
			activeDictionary,
			dictionaries,
			showSettingsDialogue,
			lookupCrossRefHandled,
			showAddDictionaryDialogue,
			dictionaryFormats,
			newDictionaryDisplayName,
			newDictionaryFilename,
			newDictionaryFormat,
			validationError,
			editedDictionary,
			editedDictionaryDisplayName
		}
	},

	methods: {
		async searchTermChanged() {
			if (this.searchTerm.length === 0) {
				// Fill wordList with ten blanks
				this.wordList = Array(10).fill('')
			} else {
				await fetch(`${SERVER_URL}/api/metadata/entry_list/${this.activeDictionary.name}/${this.searchTerm}`)
					.then((response) => response.json())
					.then((data) => {
						this.wordList = data
					})
			}
		},
		async search(word) {
			if (word.length === 0) {
				return
			}

			// Clean up previous scripts
			const scripts = document.querySelectorAll('script')
			scripts.forEach((script) => {
				script.remove()
			})

			const response = await fetch(`${SERVER_URL}/api/lookup/${this.activeDictionary.name}/${word}`)
			this.definition = await response.text().then((text) => {
				// Fix an error where the dynamically loaded script is not executed
				const scriptSrcMatches = [...text.matchAll(/<script.*?src=["'](.*?)["']/gi)]
				const scriptSrcs = scriptSrcMatches.map((match) => match[1])
				if (scriptSrcs.length !== 0) {
					scriptSrcs.forEach((src) => {
						const script = document.createElement('script')
						script.src = src
						document.body.appendChild(script)
					})
				}
				return text
			})

			if (this.searchHistory.includes(word)) {
				this.searchHistory.splice(this.searchHistory.indexOf(word), 1)
			}
			if (this.searchHistory.unshift(word) > this.historySize) {
				this.searchHistory.pop()
			}

			// Update the whole history list
			await fetch(`${SERVER_URL}/api/metadata/history`, {
				method: 'PUT',
				headers: {
					'Content-Type': 'application/json'
				},
				// The body is just an array of strings
				body: JSON.stringify(this.searchHistory)
			})

			// TODO: come up with a more elegant way to handle this
			if (!this.lookupCrossRefHandled) {
				document.addEventListener('click', (event) => {
					if (event.target.matches('a')) {
						const href = event.target.getAttribute('href')
						if (href && href.startsWith('/lookup')) {
							event.preventDefault()
							const word = href.split('/').pop().split('#')[0]
							this.search(word)
						}
					}
				})
				this.lookupCrossRefHandled = true
			}
		},
		activeDictionaryChanged(dictionary) {
			this.activeDictionary = dictionary
			this.searchTermChanged()
		},
		async historySizeChanged() {
			let needUpdate = false
			if (this.historySize < 0) {
				this.historySize = 0
				needUpdate = true
			}
			if (this.searchHistory.length > this.historySize) {
				this.searchHistory.splice(this.historySize)
				needUpdate = true
			}

			await fetch(`${SERVER_URL}/api/metadata/history_size`, {
				method: 'PUT',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					history_size: this.historySize
				})
			})

			if (needUpdate) {
				await fetch(`${SERVER_URL}/api/metadata/history`, {
					method: 'PUT',
					headers: {
						'Content-Type': 'application/json'
					},
					body: JSON.stringify(this.searchHistory)
				})
			}
		},
		getHistory() {
			// Export JSON, should be downloaded as an 'attachment'
			const historyBlob = new Blob([JSON.stringify(this.searchHistory)], {type: 'application/json'})
			const link = document.createElement('a')
			link.href = URL.createObjectURL(historyBlob)
			link.download = 'history.json'
			link.click()
			URL.revokeObjectURL(historyBlob)
		},
		dragStart(index) {
			this.draggedIndex = index
		},
		dragOver(index) {
			index
			event.preventDefault()
			event.target.classList.add('drag-over')
		},
		async drop(index) {
			event.preventDefault()
			event.target.classList.remove('drag-over')
			const draggedDictionary = this.dictionaries[this.draggedIndex]
			this.dictionaries.splice(this.draggedIndex, 1)
			this.dictionaries.splice(index, 0, draggedDictionary)

			// Update the whole dictionary list
			await fetch(`${SERVER_URL}/api/metadata/dictionary_list`, {
				method: 'PUT',
				headers: {
					'Content-Type': 'application/json'
				},
				// TODO: maybe we should have used uniform property names?
				body: JSON.stringify(this.dictionaries.map((dictionary) => {
					return {
						dictionary_display_name: dictionary.displayName,
						dictionary_name: dictionary.name,
						dictionary_format: dictionary.format,
						dictionary_filename: dictionary.filename
					}
				}))
			})
		},
		async addDictionary() {
			if (this.newDictionaryDisplayName.length === 0) {
				this.validationError = 'Dictionary name cannot be empty.'
				return
			}
			if (this.newDictionaryFilename.length === 0) {
				this.validationError = 'File name cannot be empty.'
				return
			}
			if (this.dictionaryFormats.indexOf(this.newDictionaryFormat) === -1) {
				this.validationError = 'Invalid dictionary format.'
				return
			}

			// Use the API to validate again
			await fetch(`${SERVER_URL}/api/metadata/validator/dictionary_info`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					dictionary_display_name: this.newDictionaryDisplayName,
					dictionary_name: this.newDictionaryFilename.split('/').pop().split('.')[0],
					dictionary_format: this.newDictionaryFormat,
					dictionary_filename: this.newDictionaryFilename
				})
			})
				.then((response) => response.json())
				.then((data) => {
					if (data['valid']) {
						this.dictionaries.push({
							displayName: this.newDictionaryDisplayName,
							name: this.newDictionaryFilename.split('/').pop().split('.')[0],
							format: this.newDictionaryFormat,
							filename: this.newDictionaryFilename
						})
						this.newDictionaryDisplayName = ''
						this.newDictionaryFilename = ''
						this.newDictionaryFormat = ''
						this.showAddDictionaryDialogue = false

						// Update the whole dictionary list
						fetch(`${SERVER_URL}/api/metadata/dictionary_list`, {
							method: 'PUT',
							headers: {
								'Content-Type': 'application/json'
							},
							body: JSON.stringify(this.dictionaries.map((dictionary) => {
								return {
									dictionary_display_name: dictionary.displayName,
									dictionary_name: dictionary.name,
									dictionary_format: dictionary.format,
									dictionary_filename: dictionary.filename
								}
							}))
						})
					} else {
						this.validationError = 'Dictionary info is rejected by the server.'
					}
				})
		},
		async commitNameChange() {
			if (this.editedDictionaryDisplayName.length === 0) {
				this.validationError = 'Dictionary name cannot be empty.'
				return
			}

			this.editedDictionary.displayName = this.editedDictionaryDisplayName
			this.editedDictionary = {}
			this.editedDictionaryDisplayName = ''

			// Update the whole dictionary list (there's no way to update a single entry, for now)
			await fetch(`${SERVER_URL}/api/metadata/dictionary_list`, {
				method: 'PUT',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(this.dictionaries.map((dictionary) => {
					return {
						dictionary_display_name: dictionary.displayName,
						dictionary_name: dictionary.name,
						dictionary_format: dictionary.format,
						dictionary_filename: dictionary.filename
					}
				}))
			})
		},
		async deleteDictionary(dictionary) {
			await fetch(`${SERVER_URL}/api/metadata/dictionary_list`, {
				method: 'DELETE',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					dictionary_display_name: dictionary.displayName,
					dictionary_name: dictionary.name,
					dictionary_format: dictionary.format,
					dictionary_filename: dictionary.filename
				})
			})
			this.dictionaries.splice(this.dictionaries.indexOf(dictionary), 1)
		}
	}
}
</script>
<style>
.container {
	display: flex;
	flex-direction: row;
	justify-content: space-between;
	align-items: stretch;
	border: 1px solid #ccc;
}

.left-pane {
	display: flex;
	flex-direction: column;
	justify-content: flex-start;
	align-items: stretch;
	width: 20%;
	border: 1px solid #ccc;
	overflow: scroll;
}

input {
	width: 100%;
	margin: 8px 0;
	box-sizing: border-box;
}

.lookup-area {
	border: 1px solid #ccc;
	height: 33vh;
}

button {
	margin: 0.2rem 0.2rem 0.2rem 0.2rem;
	border: 1px solid #ccc;
	border-radius: 0.25rem;
}

button:hover {
	cursor: pointer;
}

.lookup-area ul, .history-area ul, .right-pane ul, .dialogue ul {
	margin: 0 !important;
	padding: 0 !important;
}

.lookup-area ul li, .history-area ul li, .right-pane ul li {
	cursor: pointer;
	list-style-type: none !important;
	border: 1px solid #ccc !important;
	height: 1.5rem !important;
	overflow: hidden !important;
}

.dialogue ul li {
	cursor: pointer;
	list-style-type: none !important;
	border: 1px solid #ccc !important;
	height: 2rem !important;
	overflow: hidden !important;
}

.history-area {
	height: 63vh;
	overflow: scroll;
}

#history-heading, #dictionaries-heading {
	background-color: lightgrey;
	position: sticky;
	top: 0;
}

.middle-pane {
	display: flex;
	flex-direction: column;
	align-items: center;
	width: 50%;
	height: 96vh;
	border: 1px solid #ccc;
	overflow: scroll;
}

.middle-pane div {
	width: 98%;
}

/* TODO: use proper styling for audio element */
audio {
	height: 0.8em;
	/* width: 0.8em; */
}

.right-pane {
	display: flex;
	flex-direction: column;
	justify-content: flex-start;
	align-items: stretch;
	width: 30%;
	height: 96vh;
	border: 1px solid #ccc;
	overflow: scroll;
}

.active {
	font-weight: bold;
}

.dialogue {
	position: fixed;
	top: 50%;
	left: 50%;
	width: 30%;
	max-height: 70%;
	transform: translate(-50%, -50%);
	background-color: #fff;
	border: 1px solid #ccc;
	padding: 1rem;
}
</style>