# Kencode

**Kencode** is a voice-based programming approach that maps programming instructions into vocal instructions, ensuring that spoken commands align directly with Python (or any programming) syntax. This dual mapping makes it possible to move seamlessly from code → voice and from voice → code, enabling both accessibility and precise software development.

It classifies Python statements into four categories:

* **Keywords [K]:** core Python keywords (e.g., `if`, `class`, `def`, `in`, `not`)
* **Operations [O]:** operators (e.g., `+`, `-`, `=`, `>=`, `not`,`+=`, `and`)
* **Base-words [B]:** descriptor word in vocal instructions that clarifies the data type, role, or structure of a code element. (e.g., `string`, `variable`, `list`, `index`, `key`, `value`)
* **Words [W]:** user-defined names or values or not [K][O][B].

This structured mapping reduces **ambiguity in speech recognition** and ensures that vocal commands consistently map and generate valid Python code.


---
## 🌐 Try It Online

A dedicated webpage is available where users can **translate Python code into Kencode sequences and vocal instructions**.
On this page, you simply enter Python code, and the system automatically generates:

* The **Kencode sequence** (tokens like `[B]` for base-words, `[K]` for keywords, `[O]` for operators, `[W]` for words).
* The corresponding **Kencode vocal instruction (KVI)**, which represents the code in spoken form.

The user just needs to add the **proper term for `[B]` Base-words** to complete the vocal instruction naturally.

Visit the [Kencode page](https://khalidalkhaldi.pythonanywhere.com/).

---

## ⚙️ Operations Used in Kencode

Kencode supports a variety of operators across categories:

### Arithmetic

* `+` → *plus, add*
* `-` → *minus*
* `*` → *times, multiply*
* `/` → *divided by, over*
* `%` → *modulo, mod*
* `//` → *floor division*
* `**` → *exponentiation*

### Comparison

* `==` → *equal to*
* `!=` → *not equal to*
* `<` → *less than*
* `>` → *greater than*
* `<=` → *less than or equal to*
* `>=` → *greater than or equal to*

### Logical

* `and` → *and*
* `or` → *or*
* `not` → *not*
* `in` → *in*

### Assignment

* `=` → *equal, assign*
* `+=` → *add and assign*
* `-=` → *subtract and assign*
* `*=` → *multiply and assign*
* `/=` → *divide and assign*
* `//=` → *floor divide and assign*
* `%=` → *modulus and assign*

### Formatting

* **Indentation** → *tab*
* **Escape Sequence** → *octal, hex*

### Punctuations

* `#` → *comment*
* `'''` / `"""` → *document (docstring)*
---

## 📏 Kencode General Rule

The structure of a valid Kencode instruction is defined by the **Kencode General Rule (KGR):**

<img width="871" height="52" alt="Screenshot 2025-09-09 at 3 55 06 PM" src="https://github.com/user-attachments/assets/a239d72a-102d-466f-915a-921c4beea1fc" />

**Where:**

* `(?:\d*)?`: Matches an optional digit prefix that represents the **indentation level**.

  * `\d*`: Matches zero or more digits (e.g., `1`, `23`).
  * The entire group is optional, so the sequence may or may not start with a number.

* `(?:\[(?:W|B|O|K)\])*`: Matches zero or more bracketed tokens that are one of:

  * `[W]`: A **Word token**
  * `[B]`: A **Base-word token**
  * `[O]`: An **Operator token**
  * `[K]`: A **Keyword token**

   This allows for combinations like: [W][O][B][W]

* `([W|K])`: The final token in the sequence must be one of `[W]` or `[K]`.

  * This prevents sequences from ending with `[B]` or `[O]`.
  * Ensures the sequence concludes with a **syntactically complete and valid token**.


---

## 📝 Examples

# Example of Applying Kencode Approach to Python Code  

| **Python Code** | **Kencode Sequence** | **Kencode Vocal Instruction** |
|-----------------|----------------------|--------------------------------|
| `student = 'James'` | [W][O][B][W] | Student equals string James |
| `name = person.name` | [W][O][B][W][B][W] | name equals object person attribute name |
| `ticket_price = 7` | [W][W][O][B][W] | Ticket price equals digit seven |
| `print(total_cost)` | [K][B][W][W] | Print variable total cost |
| `self.species = species` | [K][B][W][O][B][W] | self attribute species equals variable species |
| `print(5+result)` | [K][B][W][O][B][W] | Print digit five plus variable result |
| `random = list(range(10, 50))` | [W][O][B][W][B][B][W][B][B][W][B][W] | random equals call list pass call range pass digit 10 digit 50 |
| `with open('data.txt') as file:` | [K][B][W][B][B][W][W][W][K][B][W] | with call open pass string data dot txt as variable file |
| `if customer['age'] > 30:` | [K][B][W][B][B][W][O][B][W] | If customer key string age greater than digit thirty |
| `customer = {'name': 'John Doe', 'age': 30}` | [W][O][B][B][W][B][B][W][W][B][B][W][B][B][W] | Customer equals key string name value string John Doe key string age value digit 30 |
| `if student_1 == student_2:` | [K][B][W][W][O][B][W][W] | If variable student one equals variable student two |
| `cat = Animal('Cat', 3)` | [W][O][B][W][B][B][W][B][W] | cat equals call animal pass string cat digit 3 |
| `cat.make_sound()` | [W][B][W][W] | cat call make sound |
| `print('Animal Species:', cat.species)` | [K][B][W][W][B][W][B][W] | print string animal species object cat attribute species |
| `if product[1] in inventory:` | 1 [B][K][B][W][B][B][W][K][B][W] | 1 tab if product index digit 1 in variable inventory |

---

With **Kencode**, developers can **program hands-free** while maintaining accuracy and readability, making it especially valuable for **accessibility and AI-driven programming research**.

---
