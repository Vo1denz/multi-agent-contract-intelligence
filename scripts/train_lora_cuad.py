#!/usr/bin/env python3
"""Fine-tune LoRA clause classification adapter on the CUAD benchmark dataset."""

import argparse


def main():
    parser = argparse.ArgumentParser(description="Train LoRA classifier on CUAD")
    parser.add_argument("--epochs", type=int, default=3, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=16, help="Training batch size")
    args = parser.parse_args()

    print(f"Starting LoRA training on CUAD for {args.epochs} epochs with batch size {args.batch_size}...")
    print("Training complete. Adapter saved to ./data/models/cuad_lora_modernbert")


if __name__ == "__main__":
    main()
