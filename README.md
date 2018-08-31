# Overview

`passman` is an inconvenient way to store your passwords.

It offers no UI beyond the command line, you can't sync it to your devices, and it has no aspirations towards being perfectly secure.

Please read the disclaimer.

## Requirements

- `virtualenvwrapper` - at least, to follow the installation instructions. If you know a different way of creating virtual environments then adjust accordingly.

## Installation

- `git clone` the repo
- `mkvirtualenv --python=python3 passman`
- `pip install .`

## Usage

The help command aims to be comprehensive. All of your questions will be answered there.

Briefly, you should

- `passman init`
- `passman create_vault --vault_name=default`

You'll be prompted for a password.

After that:

- `passman --help`

## Disclaimer

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.