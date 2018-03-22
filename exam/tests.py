<div id="example-5">
  <select v-model="selected">
    <option disabled value="">请选择</option>
    <option>A</option>
    <option>B</option>
    <option>C</option>
  </select>
  <span>Selected: {{ selected }}</span>
</div>

<script>
new Vue({
  el: '#example-5',
  data: {
    selected: ''
  }
})
</script>