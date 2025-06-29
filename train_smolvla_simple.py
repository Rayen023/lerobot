"""
python lerobot/scripts/train.py --policy.path=lerobot/smolvla_base --dataset.repo_id=lerobot/svla_so101_pickplace --batch_size=64 --steps=20000 --output_dir=outputs/train/my_smolvla --job_name=my_smolvla_training --policy.device=cuda --wandb.enable=true
python lerobot/scripts/train.py --policy.path=lerobot/smolvla_base --dataset.repo_id=lerobot/stanford_kuka_multimodal_dataset --batch_size=64 --steps=20000 --output_dir=outputs/train/kuka_smolvla --job_name=kukasmolvla_training --policy.device=cuda --wandb.enable=true
"""

# !huggingface-cli login
