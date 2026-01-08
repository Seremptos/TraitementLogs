<script setup>
</script>

<template>
  <div class="box error-box" v-show="error.httpstatus">
    <h3>Erreur !</h3>
    <p v-show="error.msg">Message : {{ error.msg }}</p>
    <p>Statut HTTP : {{error.httpstatus}}</p>
  </div>
  <div class="box success-box" v-show="success">
    <h3>Succès !</h3>
  </div>
  <main>
    <h1>Site upload logs et recherche</h1>

    <h2>Upload des logs</h2>
    <form @submit.prevent="submitForm">
      <div>
        <label for="csv">Fichier de log :</label>
        <input type="file" id="csv" name="file" accept="text/csv" v-on:change="handleFile" required/>
      </div>
      <button type="submit">Envoyer</button>
    </form>


    <h2>Recherche de logs</h2>
    <form>
      <div>
        <label for="field">Champ à rechercher :</label>
        <input id="field" v-model="queryParams.field" type="text" required/>
      </div>
      <div>
        <label for="query">Ce qu'on recherche :</label>
        <input id="query" v-model="queryParams.query" type="text" required/>
      </div>
      <div>
        <label for="order">Champ sur lequel trier :</label>
        <input id="order" v-model="queryParams.order" type="text" required/>
      </div>
      <button type="button" v-on:click="queryLogs(queryParams.field, queryParams.query, queryParams.order, queryParams.limit, queryParams.offset)">Query</button>
    </form>

    <div v-if="json">
      <table>
        <thead>
        <tr>
          <th v-for="header in allHeaders">{{ header }}</th>
        </tr>
        </thead>
        <tbody>
        <tr v-for="item in json">
          <td v-for="header in allHeaders">{{ item[header] }}</td>
        </tr>
        </tbody>
      </table>
    </div>

  </main>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      error: {
        msg: null,
        httpstatus: null
      },
      formData: {
        file: null,
      },
      success: false,
      json: null,
      queryParams: {
        field: null,
        query: null,
        order: null,
        limit: 10,
        offset: 0
      }
    };
  },

  computed: {
    allHeaders() {
      const headers = new Set();
      this.json.forEach(item => {
        Object.keys(item).forEach(key => headers.add(key));
      });
      return [...headers]; // Convert the set to an array
    }
  },
  methods: {
    submitForm() {
      this.error.msg = null
      this.error.httpstatus = null
      this.success = false

      if(this.formData.file === null) {
        console.log("No file in input!")
        return;
      }

      const config = {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }

      axios.post("http://localhost:5000/process", this.formData, config)
          .then((response) => {
            console.log(response);
            this.success = true;
          })
          .catch((error) => {
            this.handleErrors(error)
          });
    },
    handleFile(event) {
      this.formData.file = event.target.files[0];
    },

    queryLogs(field, whatToSearchFor, fieldToOrderBy = field, limit = 10, offset = 0) {
      this.error.msg = null
      this.error.httpstatus = null
      this.success = false

      axios.get(`http://localhost:5000/search/${field}/${whatToSearchFor}/${fieldToOrderBy}/${limit}/${offset}`)
          .then((response) => {
            console.log(response.data)
            this.json = response.data
          })
          .catch((error) => {
            this.handleErrors(error)
          })
    },

    handleErrors(error) {
      if(error.response) {
        this.error.msg = error.response.data;
        this.error.httpstatus = error.response.status + " " + error.response.statusText;
      } else {
        this.error.msg = "An error occured while contacting the backend."
        this.error.httpstatus = 503 + " Service Unavailable"
      }
    }
  }
};
</script>
