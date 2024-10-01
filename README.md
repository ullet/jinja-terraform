# jinja-terraform
A little experiment in using Jinja templates with Terraform.

A Python script to 'compile' template source files into working Terraform configuration files. There isn't actually anything Terraform specific in the code. The script will work with any Jinja templates, provided the files have a '.js' extension.

## Run it

``` bash
python compile-terraform.py <source_dir> <output_dir>
```
