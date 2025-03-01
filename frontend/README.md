#### to call tests
* conda activate deep-dive 
* cd ~/Code/LLM/DeepDive/frontend
```
 $npx ava 
```
npx ava path/to/test-file.js --match='specific test description'
npx ava -m 'getAvailableModels'


npx ava "src/test/**/*-test.mjs" -m 'getActiveChat Test'
